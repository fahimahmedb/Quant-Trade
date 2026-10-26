# CLAUDE — ECONOMIC QUESTION / FALSIFICATION MAP — 2026-09-21

ROLE: Economic Question Architect / Falsification Mapper.
MISSION TYPE: READ_ONLY ECONOMIC DESIGN ANALYSIS. No code, no src/tests/scripts/schema/workflow/P0/host/capital mutation performed.

```text
ECONOMIC_PROGRESS = turned the North Star wealth objective into a bounded, prioritized
  question -> evidence -> decision -> action -> learning map spanning
  Forward -> Research -> Economic -> SIZE -> RISK -> FILLS -> BOOK -> Learning.
REMAINING_BLOCKER = SCIENCE_EFFECT_ESTIMATE_CONTRACT = BLOCKED_MISSING_SCIENTIFIC_ESTIMATOR
  (per handoff/BLUE_RESEARCH_FROZEN_EFFECT_ESTIMATE_PRESTAGE_RECEPTION_2026-09-21.md);
  no newer scientific-estimator spec found on any branch as of this mission's fetch.
EXIT_CONDITION = every question below has estimand, observables, provenance/admissibility,
  falsification test, decision, action, persistence, learning consequence, staleness
  condition, and time-horizon class. Met in this document.
```

Authority chain read: `QUANT_NORTH_STAR.md`, `handoff/BLUE_PROJECT_REACQUISITION_2026-09-21.md`,
`handoff/BLUE_RESEARCH_FROZEN_EFFECT_ESTIMATE_PRESTAGE_RECEPTION_2026-09-21.md`. No newer
scientific-estimator delivery exists beyond the blocked prestage; this map does not
duplicate or replace that lane — it only defines what the eventual estimator's output
must be able to answer.

---

## 1. Question families

Notation: `[H]` = time-horizon class, `[P]` = priority class (see §5).

### Q1 — Does the effect exist?

- Plain question: does the declared Form-4 population have a positive
  allocation-weighted gross SPY-excess effect on the frozen `delta_coordinate`?
- Estimand: `delta = E[allocation_weight_j * (R_security,j - R_SPY,j)]` over the
  declared qualifying event population, on the frozen `ALLOCATION_WEIGHTED_RATIO`
  coordinate (not net/rebalanced portfolio return).
- Observables: `delta_hat`, `(lower, upper)` interval, `confidence_level`,
  `event_count`, `delta_coordinate_hash` (binds exact coordinate definition used),
  `allocation_constructor_id`, provenance chain to raw Form-4 filings.
- PIT/provenance: allocation weights `a_j` must be constructible strictly before the
  outcome window `T_j`; filing timestamps must be point-in-time as-filed, not
  as-revised; no use of data unavailable at decision time.
- Falsification test: `INVALID_EVIDENCE` if `delta_coordinate_hash` does not match the
  frozen binding, or if `lower <= 0 <= upper` at the declared confidence (no
  detectable positive effect).
- Decision: `EFFECT_PRESENT` only if interval excludes 0 in the required direction
  AND coordinate/provenance checks pass.
- Action: `RESEARCH_MORE` (effect absent or inconclusive) | `CONTINUE` (effect present,
  pass to Q2).
- Persisted: `delta_hat`, interval, `event_count`, coordinate hash, provenance
  fingerprint, hypothesis_id.
- Learning consequence: absent/weak effect feeds Q12 (where Research should not
  search again without new information).
- Staleness: re-evaluate whenever underlying Form-4 population, allocation
  constructor, or coordinate binding version changes.
- `[H]` NOT_ANSWERABLE_IN_FIRST_SLICE (blocked — see §6). `[P]`
  MUST_ANSWER_IN_FIRST_BIG_BUILD.

### Q2 — Is the evidence valid?

- Plain question: is the Q1 estimate PIT-safe, correctly clustered, non-leaking,
  non-survivorship-biased, with valid missing-outcome/sample-use accounting?
- Estimand: admissibility state of the Q1 estimate, not a new numeric quantity.
- Observables: clustering unit and `cluster_id` set, D07-O4 overlap-resolution
  record, missing-outcome count and disposition, discovery/validation split ledger,
  trial-budget/multiplicity ledger for the lane.
- PIT/provenance: clustering geometry must not use post-outcome information to form
  clusters; missing-outcome handling must be declared before inspection of results.
- Falsification test: any leakage path found (allocation formed after outcome
  window opens), clustering unit undeclared or outcome-dependent, or multiplicity
  budget exceeded without correction.
- Decision: `VALID_EVIDENCE | INVALID_EVIDENCE | INSUFFICIENT_EVIDENCE`.
- Action: `INVALID_EVIDENCE` -> `KILL` hypothesis instance; `INSUFFICIENT_EVIDENCE` ->
  `RESEARCH_MORE`; `VALID_EVIDENCE` -> `CONTINUE` to Q3.
- Persisted: admissibility verdict, clustering/leakage audit record, multiplicity
  ledger entry.
- Learning consequence: recurring `INVALID_EVIDENCE` causes on a given constructor
  pattern should down-rank that Research lane (feeds Q12).
- Staleness: invalid if underlying admissibility rules (D07-O4 geometry, sample-use
  accounting policy) are revised after the verdict was recorded.
- `[H]` NOT_ANSWERABLE_IN_FIRST_SLICE (blocked — see §6). `[P]`
  MUST_ANSWER_IN_FIRST_BIG_BUILD.

### Q3 — Is it developmental or forward-confirmed?

- Plain question: has this hypothesis only been observed on data used during its
  own discovery (`DEVELOPMENT`), or has it since been observed on genuinely new,
  independent, forward-in-time data (`FORWARD_CONFIRMATION`)?
- Estimand: binary evidence-maturity state, bound to explicit sample partitions.
- Observables: discovery sample window, forward sample window(s), non-overlap
  proof between them, count of independent forward observations.
- PIT/provenance: forward sample must be strictly outside the discovery sample's
  observation and tuning window; no hypothesis re-selection after seeing forward
  data.
- Falsification test: any overlap between discovery and "forward" windows, or any
  re-tuning of the hypothesis/coordinate definition after forward data was visible,
  voids `FORWARD_CONFIRMATION`.
- Decision: `DEVELOPMENT | FORWARD_CONFIRMATION`. No automatic promotion merely
  because a `ForwardObservation` record exists — promotion requires the
  non-overlap proof above plus a minimum independent forward-sample count (set by
  the eventual scientific spec; treated as `FUTURE_FIELD` here).
- Action: `DEVELOPMENT` -> `SHADOW` at most (no capital-relevant weight beyond
  paper tracking); `FORWARD_CONFIRMATION` -> eligible to `CONTINUE` to Q4.
- Persisted: evidence-maturity label, sample-window boundaries, forward
  observation count, promotion timestamp.
- Learning consequence: a hypothesis that never reaches `FORWARD_CONFIRMATION`
  after N opportunities is a candidate for `RETIRE` and a Q12 negative signal.
- Staleness: label must be re-derived, not cached, whenever new forward samples
  arrive (it can move forward but the underlying non-overlap proof must still hold).
- `[H]` AFTER_FIRST_SHADOW_DECISION (development label) /
  AFTER_REPEATED_FORWARD_SAMPLE (forward-confirmation label). `[P]`
  MUST_ANSWER_IN_FIRST_BIG_BUILD (the DEVELOPMENT label only; forward-confirmation
  itself is DEFER_UNTIL_REPEATED_FORWARD_EVIDENCE).

### Q4 — Does the effect survive real frictions?

- Plain question: after spread, commission, impact, participation and other
  modeled costs, does the effect remain economically positive?
- Estimand: `economic_margin = delta_hat - modeled_cost(size, liquidity, venue)`
  evaluated under the authoritative ExecutionModel, both pre-sizing (cost-model
  compatibility check) and post-sizing/pre-fill (implied-participation recheck).
- Observables: `cost_model_identity`, `pre_size_cost_consistency`,
  `post_size_participation`, `post_size_cost_consistency`, `economic_margin`.
- PIT/provenance: cost model parameters must be the ones in force at decision
  time, not retrospectively fitted; participation must use point-in-time
  liquidity/volume data.
- Falsification test: `MODEL_INCOMPATIBLE` if the cost model cannot be evaluated
  for the declared instrument/venue/size at all; `NO_TRADE_COSTS` if
  `economic_margin <= 0` at either check.
- Decision: `ECONOMIC_CONTINUE | NO_TRADE_COSTS | MODEL_INCOMPATIBLE`.
- Action: `ECONOMIC_CONTINUE` -> `CONTINUE` to Q5; `NO_TRADE_COSTS` -> `NO_TRADE`
  with reason code; `MODEL_INCOMPATIBLE` -> `RESEARCH_MORE` (fix cost-model
  binding) or `KILL` if structurally unfillable.
- Persisted: `economic_margin`, both consistency flags, cost_model_identity,
  decision + reason codes.
- Learning consequence: recurring `NO_TRADE_COSTS` on a given instrument class
  informs Q12 (frictions dominate there; deprioritize).
- Staleness: re-check required whenever cost model version, venue liquidity
  regime, or declared size changes materially before fill.
- `[H]` AFTER_FIRST_SHADOW_DECISION. `[P]` MUST_ANSWER_IN_FIRST_BIG_BUILD.

### Q5 — How large is economically justified?

- Plain question: given the validated, friction-surviving effect, what exposure
  is justified?
- Estimand: `economic_size` from the single Economic MarginSizingRule (no second
  sizing authority), then `final_pre_risk_size = min(economic_size,
  lifecycle_cap)`.
- Observables: `economic_margin` (from Q4), uncertainty/interval width,
  capacity/liquidity constraint, `lifecycle_cap`, current deployed capital state
  from the Book.
- PIT/provenance: capital state must be the current persistent Book snapshot, not
  a stale or simulated-fresh balance.
- Falsification test: `MODEL_INCOMPATIBLE` state from Q4 propagates — sizing must
  refuse to run on an unresolved cost-model state; a computed size exceeding
  `lifecycle_cap` before clamping is a defect, not a valid output.
- Decision: `economic_size`, `lifecycle_cap`, `final_pre_risk_size` all recorded;
  no separate "vet" sizing decision permitted elsewhere.
- Action: proceed to Q6 with `final_pre_risk_size`, or `NO_TRADE` if
  `final_pre_risk_size` rounds to zero.
- Persisted: `economic_size`, `lifecycle_cap`, `final_pre_risk_size`,
  sizing-rule version identity.
- Learning consequence: systematic clamping by `lifecycle_cap` rather than by
  margin signals a capacity constraint worth surfacing to Research/Build, not an
  edge-quality problem.
- Staleness: invalid if Book capital state used is older than one control-plane
  tick at decision time.
- `[H]` AFTER_FIRST_SHADOW_DECISION. `[P]` MUST_ANSWER_IN_FIRST_BIG_BUILD.

### Q6 — Does the opportunity improve the current portfolio?

- Plain question: given current Book exposures, correlation and concentration,
  should Risk approve, scale down, or veto this candidate?
- Estimand: post-transform, post-scale portfolio state that would actually result
  if this candidate is admitted at `final_pre_risk_size` (per North Star: Risk
  approval must describe the *final* simulated portfolio, not the standalone
  candidate).
- Observables: current Book positions/exposures, correlation/overlap of this
  candidate's instrument(s) with existing sleeves, concentration limits,
  strategy-level attribution (multiple strategies on the same instrument tracked
  separately, then aggregated for portfolio state).
- PIT/provenance: Book snapshot must be current; correlation estimates must use
  data available at decision time.
- Falsification test: a `risk_verdict` computed from standalone candidate risk
  only (ignoring existing Book exposure) is invalid by construction.
- Decision: `approve | scale_down | veto`, with `risk_adjusted_size` when
  scaled.
- Action: `approve`/`scale_down` -> `CONTINUE` to Q7; `veto` -> `NO_TRADE` with
  reason code.
- Persisted: `risk_verdict`, `risk_adjusted_size`, concentration/correlation
  snapshot used.
- Learning consequence: frequent vetoes concentrated in one sleeve/instrument
  class feed Q12 (diversify search away from saturated exposure).
- Staleness: re-check required if Book state changes materially between Risk
  evaluation and fill attempt.
- `[H]` AFTER_FIRST_SHADOW_DECISION. `[P]` MUST_ANSWER_IN_FIRST_BIG_BUILD.

### Q7 — Is TRADE superior to NO_TRADE?

- Plain question: given effect, uncertainty, frictions, size, capacity and Risk
  verdict, is expected future wealth better with action than without?
- Estimand: `expected_wealth_delta = risk_adjusted_size * economic_margin -
  expected_execution_shortfall`, compared against 0.
- Observables: all upstream fields from Q1–Q6, plus expected execution shortfall
  estimate from the ExecutionModel.
- PIT/provenance: inherits all upstream provenance; no new data source.
- Falsification test: a `TRADE` action recorded with `expected_wealth_delta <= 0`
  and no override reason code is invalid.
- Decision: `TRADE | NO_TRADE`, with explicit NO_TRADE reason codes drawn from a
  closed set (e.g. `EFFECT_ABSENT`, `EVIDENCE_INVALID`, `COST_DOMINATED`,
  `RISK_VETO`, `CAPACITY_ZERO`).
- Action: `TRADE` -> `CONTINUE` to Q8 (dispatch to FILLS); `NO_TRADE` -> persist
  and route to Q11 eligibility.
- Persisted: `expected_wealth_delta`, action, reason_codes, full Decision Card
  (§3).
- Learning consequence: this is the canonical decision point Learning attaches
  outcomes to (via Q9/Q10/Q11).
- Staleness: decision is valid only for the tick/session it was computed in; a
  stale decision must not be executed against a changed Book/market state.
- `[H]` AFTER_FIRST_SHADOW_DECISION. `[P]` MUST_ANSWER_IN_FIRST_BIG_BUILD.

### Q8 — Did execution preserve the expected edge?

- Plain question: comparing expected vs. modeled/realized shadow fill, did
  spread/slippage/impact, capacity truncation and delay erode the edge?
- Estimand: `execution_shortfall = expected_fill_value - realized_shadow_fill_value`
  (modeled, in shadow mode).
- Observables: expected price/size at decision time, realized shadow fill
  price/size/timestamp, capacity truncation flag, delay duration.
- PIT/provenance: realized fill must be logged at actual shadow-fill time, not
  backfilled or re-simulated after the fact.
- Falsification test: `EDGE_ERASED_BY_EXECUTION` if `execution_shortfall >=
  economic_margin * risk_adjusted_size`; `EDGE_DEGRADED` if shortfall is
  material but does not fully erase margin; else `EDGE_PRESERVED`.
- Decision: `EDGE_PRESERVED | EDGE_DEGRADED | EDGE_ERASED_BY_EXECUTION`.
- Action: `EDGE_ERASED_BY_EXECUTION` repeatedly on an instrument/venue ->
  `SCALE_DOWN` or `RETIRE` that venue/size combination; otherwise `CONTINUE` to
  Q9.
- Persisted: `execution_shortfall`, fill comparison record, decision.
- Learning consequence: systematic erosion feeds Q12 (search should avoid
  instruments/venues with structurally poor execution quality) and back into the
  ExecutionModel's own calibration (outside this mission's scope to implement).
- Staleness: not stale — this is a point-in-time realized comparison, permanent
  once logged.
- `[H]` ONLY_AFTER_LIVE/REAL_EXECUTION for true fill comparison; a shadow-fill
  approximation is AFTER_FIRST_SHADOW_DECISION. `[P]`
  MUST_ANSWER_IN_FIRST_BIG_BUILD (shadow form) / DEFER_UNTIL_LIVE_EXECUTION (real
  fill form).

### Q9 — Did the decision increase wealth?

- Plain question: measured in the persistent Book after modeled frictions, did
  this decision's net contribution to wealth increase?
- Estimand: `realized_wealth_contribution = net_pnl_after_frictions` attributable
  to this specific Book operation, isolating it from concurrent market drift.
- Observables: `book_operation_id`, position P&L, fees/spread/slippage actually
  applied, holding-period benchmark return (SPY or relevant beta) for drift
  isolation.
- PIT/provenance: must read from the persistent Book ledger, restart-safe and
  idempotent (no duplicate counting across crash/replay).
- Falsification test: a positive raw P&L that is fully explained by benchmark
  drift (i.e. `realized_wealth_contribution` net of benchmark is <= 0) must not
  be counted as discovered alpha.
- Decision: `wealth_increased: bool`, plus `drift_adjusted_contribution`.
- Action: feeds Q10 accumulation; no independent action beyond logging.
- Persisted: `realized_wealth_contribution`, `drift_adjusted_contribution`,
  `book_operation_id`, `learning_outcome_id`.
- Learning consequence: this is the raw input series for Q10 decay tracking and
  Q11 rejection correctness.
- Staleness: not stale — permanent ledger fact once the Book operation settles.
- `[H]` AFTER_FIRST_SHADOW_DECISION (shadow P&L) / ONLY_AFTER_LIVE/REAL_EXECUTION
  (real wealth). `[P]` MUST_PERSIST_FOR_LATER_LEARNING.

### Q10 — Is the edge persistent or decaying?

- Plain question: across repeated independent evidence and shadow/live
  decisions, is estimate stability, economic margin, execution quality and
  realized contribution holding up, declining, or gone?
- Estimand: trend of `{delta_hat, economic_margin, execution_shortfall,
  realized_wealth_contribution}` over an ordered sequence of independent
  observations for this hypothesis.
- Observables: time series of the above fields, keyed by `hypothesis_id`, with
  observation count.
- PIT/provenance: each observation must be the one recorded at its own decision
  time, not restated.
- Falsification test: insufficient observation count must not be silently
  treated as stability; a state enum alone (e.g. "ACTIVE") is not evidence of
  decay management per North Star integrity invariants — the trend must
  actually be computed.
- Decision: `STABLE | DECAYING | BROKEN | INSUFFICIENT_HISTORY`.
- Action: `DECAYING` -> `SCALE_DOWN`; `BROKEN` -> `RETIRE`; `STABLE` ->
  `CONTINUE`; `INSUFFICIENT_HISTORY` -> `SHADOW`/keep collecting.
- Persisted: decay-state label, trend statistics, observation count,
  `learning_outcome_id` linkage.
- Learning consequence: this is a primary Learning/Memory output — durable
  record of strategy lifecycle used to prioritize retirement/replacement.
- Staleness: re-evaluate every new observation; a decay label older than one
  full observation cycle without recomputation must not be trusted for a live
  decision.
- `[H]` AFTER_REPEATED_FORWARD_SAMPLE. `[P]` DEFER_UNTIL_REPEATED_FORWARD_EVIDENCE,
  but MUST_PERSIST_FOR_LATER_LEARNING (the raw series must be captured from the
  first decision onward even though the verdict itself defers).

### Q11 — Was a rejection correct?

- Plain question: for `NO_TRADE`/vetoed opportunities, was the rejection
  correct in hindsight, without contaminating the original prospective state?
- Estimand: counterfactual outcome had the rejected candidate been taken,
  estimated from realized market data over the same would-have-been holding
  window — computed and stored strictly as a *separate, later-labeled* record,
  never rewriting the original decision.
- Observables: original Decision Card (frozen, immutable), realized market
  outcome over the counterfactual window, reason_codes from the original
  rejection.
- PIT/provenance: the counterfactual evaluation must be clearly timestamped as
  retrospective and must never alter `expected_wealth_delta`, `action`, or any
  other field on the original Decision Card.
- Falsification test: any process that mutates the original NO_TRADE record
  in place is invalid — correctness must be a new linked record.
- Decision: `CORRECT_REJECTION | FALSE_REJECT | INDETERMINATE` (e.g. liquidity
  made the counterfactual unfillable).
- Action: no action on the closed decision itself; `FALSE_REJECT` patterns feed
  Q12 (calibrate the reason code that caused it — e.g. if `RISK_VETO` is
  frequently a false reject, that's a Risk-policy learning signal, not a license
  to reverse the original decision).
- Persisted: counterfactual outcome record, `FALSE_REJECT`/`CORRECT_REJECTION`
  label, link to original `book_operation_id`/decision record.
- Learning consequence: primary source for calibrating NO_TRADE reason-code
  quality over time.
- Staleness: the counterfactual window itself is fixed once evaluated; not
  re-evaluated, but new rejections accumulate as separate instances.
- `[H]` AFTER_REPEATED_FORWARD_SAMPLE. `[P]` DEFER_UNTIL_REPEATED_FORWARD_EVIDENCE.

### Q12 — Where should Research search next?

- Plain question: given accepted/rejected hypotheses, false positives/negatives,
  missed opportunity and execution shortfall, where should Research prioritize
  search?
- Estimand: a ranked set of search directions (instrument classes, hypothesis
  families, data sources) with associated confidence — not a guarantee of
  alpha.
- Observables: aggregated outcomes from Q1–Q11 across all hypotheses: hit/miss
  rates by category, decay rates by category, execution-quality patterns by
  venue/instrument, false-reject patterns by reason code.
- PIT/provenance: aggregation must only use data available as of the
  recommendation time; must not leak future hypothesis outcomes into the
  ranking used to justify past search.
- Falsification test: a search-priority recommendation with no underlying
  aggregated evidence record (i.e., asserted rather than derived) is invalid.
- Decision: ranked list of search directions with supporting counts.
- Action: `RESEARCH_MORE` directed at top-ranked directions; explicit
  deprioritization of consistently poor categories.
- Persisted: search-priority record, linked evidence counts, timestamp.
- Learning consequence: this closes the Learning -> Research loop from the
  North Star topology; it is the terminal consumer of all other questions'
  outcomes.
- Staleness: re-rank whenever a material number of new outcomes accumulate;
  a priority list is a recommendation, not a frozen fact.
- `[H]` AFTER_REPEATED_FORWARD_SAMPLE. `[P]` DEFER_UNTIL_REPEATED_FORWARD_EVIDENCE,
  but MUST_PERSIST_FOR_LATER_LEARNING (raw counts must be captured from
  first decisions onward).

---

## 2. Time-horizon summary table

| Q | Horizon | First-slice priority |
|---|---|---|
| Q1 | NOT_ANSWERABLE_IN_FIRST_SLICE (blocked by science contract) | MUST_ANSWER_IN_FIRST_BIG_BUILD |
| Q2 | NOT_ANSWERABLE_IN_FIRST_SLICE (blocked by science contract) | MUST_ANSWER_IN_FIRST_BIG_BUILD |
| Q3 | AFTER_FIRST_SHADOW_DECISION / AFTER_REPEATED_FORWARD_SAMPLE | MUST_ANSWER_IN_FIRST_BIG_BUILD (label only) |
| Q4 | AFTER_FIRST_SHADOW_DECISION | MUST_ANSWER_IN_FIRST_BIG_BUILD |
| Q5 | AFTER_FIRST_SHADOW_DECISION | MUST_ANSWER_IN_FIRST_BIG_BUILD |
| Q6 | AFTER_FIRST_SHADOW_DECISION | MUST_ANSWER_IN_FIRST_BIG_BUILD |
| Q7 | AFTER_FIRST_SHADOW_DECISION | MUST_ANSWER_IN_FIRST_BIG_BUILD |
| Q8 | AFTER_FIRST_SHADOW_DECISION (shadow) / ONLY_AFTER_LIVE/REAL_EXECUTION (real) | MUST_ANSWER_IN_FIRST_BIG_BUILD (shadow) / DEFER_UNTIL_LIVE_EXECUTION (real) |
| Q9 | AFTER_FIRST_SHADOW_DECISION (shadow) / ONLY_AFTER_LIVE/REAL_EXECUTION (real) | MUST_PERSIST_FOR_LATER_LEARNING |
| Q10 | AFTER_REPEATED_FORWARD_SAMPLE | DEFER_UNTIL_REPEATED_FORWARD_EVIDENCE + MUST_PERSIST_FOR_LATER_LEARNING |
| Q11 | AFTER_REPEATED_FORWARD_SAMPLE | DEFER_UNTIL_REPEATED_FORWARD_EVIDENCE |
| Q12 | AFTER_REPEATED_FORWARD_SAMPLE | DEFER_UNTIL_REPEATED_FORWARD_EVIDENCE + MUST_PERSIST_FOR_LATER_LEARNING |

---

## 3. Canonical Economic Decision Card

One record per candidate opportunity, immutable once `action` is set (Q11
counterfactuals are separate linked records, never edits to this card).

```text
hypothesis_id
research_ticket_id
sample_id
evidence_label                 # DEVELOPMENT | FORWARD_CONFIRMATION  (Q3)
delta_coordinate_hash          # binds exact frozen coordinate definition  (Q1)
delta_hat                      # (Q1)
lower
upper
confidence_level
event_count
economic_margin                # (Q4)
cost_model_identity
pre_size_cost_consistency      # bool  (Q4)
economic_size                  # (Q5)
lifecycle_cap
final_pre_risk_size
risk_verdict                   # approve | scale_down | veto  (Q6)
risk_adjusted_size
execution_model_identity
post_size_participation        # (Q4 recheck)
post_size_cost_consistency     # bool
action                         # TRADE | NO_TRADE | KILL | SCALE_DOWN | SHADOW | RETIRE | RESEARCH_MORE  (Q7)
reason_codes                   # closed set, required when action != TRADE
expected_wealth_delta          # (Q7)
book_operation_id              # (Q9, only when action == TRADE and a fill occurs)
learning_outcome_id            # link into Q9/Q10/Q11/Q12 aggregation

# FUTURE_FIELD — not yet lawfully producible pending science-contract closure:
# allocation_constructor_id, cluster_id_set, D07-O4 overlap-resolution record,
# multiplicity/trial-budget ledger entry, forward-admissibility proof reference.
```

Fields marked `FUTURE_FIELD` are flagged, not fabricated: they are required by
Q1/Q2 but cannot be populated until the scientific estimator exists (§6).

---

## 4. Falsification matrix

| Question | False positive (system wrongly says yes/good) | Detection signal | False negative (system wrongly says no/bad) | Detection signal | Affected authority | Correct response |
|---|---|---|---|---|---|---|
| Q1 | Interval computed on wrong coordinate (e.g. net portfolio return) mislabeled as `delta_hat` | `delta_coordinate_hash` mismatch against frozen binding | Real effect discarded due to underpowered/mis-clustered sample | Event count anomalously low vs. population; interval implausibly wide | Research/science | Block promotion; reject the estimate; return to Research |
| Q2 | Leakage (allocation formed post-outcome) passes as `VALID_EVIDENCE` | Audit finds allocation timestamp >= outcome window start | Valid estimate wrongly marked `INVALID_EVIDENCE` from overly conservative admissibility rule | Manual admissibility re-derivation contradicts automated verdict | Research/science | `KILL` the false-valid instance; re-run admissibility audit code path |
| Q3 | Overlapping discovery/forward windows mislabeled `FORWARD_CONFIRMATION` | Non-overlap proof check fails on audit | Genuinely independent forward evidence stuck at `DEVELOPMENT` due to conservative window definition | Forward sample count high but label unchanged | Research | Correct window boundaries; do not silently re-promote without re-derivation |
| Q4 | Cost model understates true frictions, `ECONOMIC_CONTINUE` on a losing trade | Post-fill realized cost >> modeled cost, repeatedly | Cost model overstates frictions, real edge wrongly killed as `NO_TRADE_COSTS` | Realized shadow fills show margin available that model predicted absent | Economic/ExecutionModel | Recalibrate cost model; do not let SIZE/RISK trust an uncalibrated model silently |
| Q5 | Sizing rule computes size from stale/wrong Book capital snapshot | Book snapshot timestamp older than one control tick | Correct opportunity sized to zero by an overly tight `lifecycle_cap` | Margin strongly positive but `final_pre_risk_size` == 0 every time | SIZE | Refuse stale-state sizing; review `lifecycle_cap` calibration, not the margin signal |
| Q6 | Risk approves based on standalone-candidate risk, ignoring correlated Book exposure | `risk_verdict` computed without reading current Book positions | Risk vetoes based on stale/incorrect correlation data | Correlation snapshot older than decision tick | RISK | Reject any risk verdict not derived from current post-transform portfolio state |
| Q7 | `TRADE` recorded despite `expected_wealth_delta <= 0` | Decision Card audit: action vs. sign of expected_wealth_delta | Systematic `NO_TRADE` despite genuinely positive expected wealth, due to overly conservative reason-code thresholds | Q11 counterfactuals show repeated `FALSE_REJECT` from one reason code | Capital Desk | Invalidate the decision; audit threshold calibration behind the over-conservative reason code |
| Q8 | Shadow fill modeled too favorably, `EDGE_PRESERVED` claimed when real execution would erase it | Shadow fill assumptions diverge from ExecutionModel's own historical realized fills | Execution wrongly blamed (`EDGE_ERASED_BY_EXECUTION`) for a shortfall actually caused by a bad Q1 estimate | Root-cause trace shows Q1 estimate itself was miscalibrated, not execution | FILLS | Recalibrate shadow-fill model; separate estimate-error from execution-error in attribution |
| Q9 | Benchmark/market drift counted as discovered wealth contribution | `drift_adjusted_contribution` not computed or ignored | Genuine alpha contribution masked by unrelated portfolio-level drawdown in the same period | Attribution not isolated to `book_operation_id` | BOOK | Never report raw P&L as alpha; always report drift-adjusted, operation-isolated contribution |
| Q10 | Decay label `STABLE` asserted from a state enum with no recomputed trend | No underlying trend statistics found behind the label (violates North Star: "a state enum is not a capability") | Genuinely decaying edge kept `STABLE` due to too few required observations before recompute | `INSUFFICIENT_HISTORY` should have applied but was skipped | Learning | Require trend computation behind every label; default to `INSUFFICIENT_HISTORY` absent it |
| Q11 | Rejected-then-would-have-lost trade wrongly labeled `FALSE_REJECT` from an unfillable counterfactual | Liquidity/capacity check on counterfactual window shows it was never actually fillable | Correct rejection mislabeled `FALSE_REJECT` due to counterfactual using unrealistic (frictionless) fill assumptions | Counterfactual cost model differs from the ExecutionModel used elsewhere | Learning | Apply the same ExecutionModel/liquidity constraints to counterfactuals as to real fills |
| Q12 | Search direction ranked high from a small, lucky sample (multiple-testing artifact) | Ranking not adjusted for sample size / multiplicity | Genuinely promising direction deprioritized from one early false-reject cluster | Ranking driven by a single reason-code spike rather than aggregated evidence | Research routing | Require minimum sample size and multiplicity correction before acting on a ranking |

---

## 5. Prioritization

Ordering rule applied: (1) ability to kill false economic positives, (2)
closeness to North Star wealth objective, (3) ability to support a real
decision, (4) dependency order.

```text
MUST_ANSWER_IN_FIRST_BIG_BUILD
  Q1, Q2  — blocked pending science contract; still first in dependency order
            and highest false-positive-kill value once unblocked
  Q3      — DEVELOPMENT label only (forward-confirmation itself defers)
  Q4      — kills false positives that survive Q1/Q2 but die on frictions
  Q5      — required to support any real decision
  Q6      — required Risk gate before any decision is real
  Q7      — the canonical TRADE/NO_TRADE decision point
  Q8      — shadow-fill form only, to validate the FILLS boundary exists

MUST_PERSIST_FOR_LATER_LEARNING
  Q9      — raw wealth-contribution series, from first shadow decision onward
  Q10     — raw trend series capture (verdict itself defers)
  Q12     — raw aggregation counts (ranking itself defers)

DEFER_UNTIL_REPEATED_FORWARD_EVIDENCE
  Q3 (forward-confirmation verdict), Q10 (verdict), Q11, Q12 (ranking)

DEFER_UNTIL_LIVE_EXECUTION
  Q8 (real-fill form), Q9 (real-wealth form)
```

Dependency chain enforced: Q1 -> Q2 -> Q3(dev) -> Q4 -> Q5 -> Q6 -> Q7 -> Q8(shadow) ->
Q9(shadow) -> {Q3(forward), Q10, Q11, Q12} once repeated samples exist -> {Q8(real),
Q9(real)} once live execution is authorized.

---

## 6. Science blocker impact

`SCIENCE_EFFECT_ESTIMATE_CONTRACT = BLOCKED_MISSING_SCIENTIFIC_ESTIMATOR` (confirmed
current at this mission's fetch; no newer scientific-estimator delivery found).

Directly blocked, cannot be lawfully answered on real data until closed:

- **Q1** — no lawful `delta_hat`/interval on the frozen coordinate exists yet;
  current Research-ticket outputs are the wrong coordinate (realized/rebalanced
  portfolio return, not `ALLOCATION_WEIGHTED_RATIO`).
- **Q2** — admissibility (clustering, leakage, multiplicity) cannot be verified
  for an estimate that does not yet lawfully exist.

Indirectly blocked (structurally dependent on Q1/Q2 output, even though their
*mechanics* — sizing rule, risk gate, decision card shape, fill/book plumbing —
can be designed and even exercised on synthetic fixtures now):

- Q4, Q5, Q6, Q7 cannot run on real evidence; a synthetic positive
  `EffectEstimate` fixture may prove integration plumbing only, and must not be
  represented as evidence that real Research currently produces the frozen
  coordinate.
- Q3's `FORWARD_CONFIRMATION` branch is meaningless without a lawful Q1/Q2 to
  confirm forward.

Not blocked by the science contract, but gated on later evidence volume
regardless:

- Q8, Q9, Q10, Q11, Q12 depend on accumulated decisions existing at all —
  they are gated by sample count, not directly by the science contract, but in
  practice cannot start until Q1/Q2 unblock the upstream chain.

Per `handoff/BLUE_RESEARCH_FROZEN_EFFECT_ESTIMATE_PRESTAGE_RECEPTION_2026-09-21.md`,
closing this blocker requires a separately authorized scientific-estimator
specification/implementation resolving: D07-O4 overlap/clustering geometry,
pre-outcome allocation constructor and `allocation_constructor_id`, security/SPY
return conventions, holding interval, corporate-action and D19/terminal
treatment, lawful `T_j` construction, sample provenance, discovery/validation
reuse accounting, lane-specific multiplicity budget, and forward-admissibility
binding. This mission does not attempt that closure and does not replace the
scientific-estimator owner.

---

## 7. ONE BIG BUILD impact

Minimum capabilities the eventual bounded build must provide so the
first-slice (MUST_ANSWER_IN_FIRST_BIG_BUILD) questions are answerable the
moment the science contract closes:

1. **Lawful EffectEstimate producer or fail-closed** — a caller that binds
   `ratio_estimate`/`cluster_bootstrap_ratio`, `aggregate_allocation_weighted`,
   and `DeltaCoordinateBinding`/`evaluate_delta_coordinate` into one estimate
   with `delta_coordinate_hash`, or explicitly fails closed
   (`EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE`) rather than silently
   substituting the wrong coordinate. Required for Q1.
2. **Admissibility audit path** — clustering/leakage/multiplicity checks
   producing `VALID_EVIDENCE | INVALID_EVIDENCE | INSUFFICIENT_EVIDENCE` as a
   distinct, inspectable verdict. Required for Q2.
3. **DEVELOPMENT vs FORWARD_CONFIRMATION state machine** — with an explicit,
   auditable non-overlap proof between discovery and forward sample windows,
   not an implicit flag. Required for Q3.
4. **Economic margin under compatible costs** — pre-sizing cost-model
   compatibility check and post-sizing/pre-fill participation recheck against
   the single authoritative ExecutionModel. Required for Q4.
5. **Single sizing authority** — one Economic MarginSizingRule plus
   lifecycle-cap clamp, with no parallel/competing sizing path. Required for
   Q5.
6. **Independent Risk veto over final portfolio state** — Risk evaluation
   reading current persistent Book exposures/correlation, not standalone
   candidate risk. Required for Q6.
7. **One shadow fill path with reason-coded NO_TRADE** — a FILLS boundary
   that records both executed and NO_TRADE outcomes with closed-set reason
   codes. Required for Q7/Q8(shadow).
8. **Persistent, restart-safe Book mutation** — idempotent under crash/replay,
   isolating drift from attributable contribution per `book_operation_id`.
   Required for Q9(shadow).
9. **Durable Decision Card persistence** — every field in §3 stored
   immutably, with `FUTURE_FIELD`s explicitly marked rather than fabricated,
   and a `learning_outcome_id` linkage ready for later Q9/Q10/Q11/Q12
   aggregation even before those verdicts are computable.
10. **Replay safety and later expected-vs-realized comparison hooks** — enough
    structure (timestamps, model-version identities) that Q8/Q9 real-execution
    forms and Q10/Q11/Q12 aggregation can be computed later without
    re-deriving history.

No implementation code is proposed here; this is a capability checklist for
the build spec that will be frozen once the science contract closes.

---

## Final summary

```text
ECONOMIC_PROGRESS = North Star wealth objective decomposed into 12 question
  families spanning Forward -> Research -> Economic -> SIZE -> RISK -> FILLS ->
  BOOK -> Learning, each with estimand, observables, PIT/provenance,
  falsification test, decision, action, persistence, learning consequence,
  staleness condition, time horizon and priority class; one canonical Decision
  Card; one falsification matrix with false-positive/false-negative modes per
  family; one prioritized first-slice ordering; one ONE-BIG-BUILD capability
  checklist.

REMAINING_BLOCKER = SCIENCE_EFFECT_ESTIMATE_CONTRACT =
  BLOCKED_MISSING_SCIENTIFIC_ESTIMATOR. Q1/Q2 cannot run on real evidence;
  Q4-Q7 cannot run on real evidence as a consequence.

EXIT_CONDITION = met for this mission's scope: every question has estimand,
  observables, provenance/admissibility, falsification test, decision, action,
  persistence, learning consequence, and deferred limits, all explicit in this
  document.

FIRST_SLICE_MUST_ANSWER = Q1, Q2 (blocked pending science contract), Q3
  (DEVELOPMENT label), Q4, Q5, Q6, Q7, Q8 (shadow form).

FIRST_SLICE_MUST_PERSIST = Q9 (shadow wealth series), Q10 (raw trend series),
  Q12 (raw aggregation counts) — captured from first decision onward even
  though their verdicts defer.

FORWARD_EVIDENCE_LATER_QUESTIONS = Q3 (FORWARD_CONFIRMATION verdict), Q10
  (verdict), Q11, Q12 (ranking).

LIVE_EXECUTION_LATER_QUESTIONS = Q8 (real-fill form), Q9 (real-wealth form).

SCIENCE_BLOCKER_IMPACT = Q1 and Q2 cannot lawfully run on real Form-4 data;
  Q4-Q7 can be exercised only on synthetic fixtures (plumbing proof, not
  evidence) until a separately authorized scientific-estimator
  specification/implementation closes the contract. This mission does not
  attempt that closure.

ONE_BIG_BUILD_CAPABILITY_REQUIREMENTS = lawful EffectEstimate producer or
  fail-closed; admissibility audit path; DEVELOPMENT/FORWARD_CONFIRMATION
  state machine with non-overlap proof; economic margin under compatible
  costs (pre- and post-sizing); single sizing authority with lifecycle cap;
  independent Risk veto over final portfolio state; one shadow fill path with
  reason-coded NO_TRADE; persistent restart-safe idempotent Book mutation;
  durable Decision Card persistence with FUTURE_FIELDs marked; replay-safety
  hooks for later expected-vs-realized comparison.

ECONOMIC_QUESTION_MAP = READY_FOR_BLUE_REVIEW
```

Return control to Blue.
