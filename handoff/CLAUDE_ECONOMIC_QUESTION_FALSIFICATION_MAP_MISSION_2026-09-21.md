# CLAUDE — ECONOMIC QUESTION / FALSIFICATION MAP MISSION — 2026-09-21

ROLE: Economic Question Architect / Falsification Mapper.

Repository: fahimahmedb/Quant-Trade
Work only on: parallel/claude-economic-question-falsification-map-2026-09-21
Do not create another branch.

MISSION TYPE:
READ_ONLY ECONOMIC DESIGN ANALYSIS + QUESTION MAP + FALSIFICATION FRAMEWORK

At the beginning and end of the handoff record:
ECONOMIC_PROGRESS =
REMAINING_BLOCKER =
EXIT_CONDITION =

For this mission:
ECONOMIC_PROGRESS = turn the North Star into a bounded set of economic questions that Quant can answer and act on.
REMAINING_BLOCKER = architecture/spec work exists, but there is no explicit question -> evidence -> decision -> action -> learning map.
EXIT_CONDITION = a complete prioritized map exists where every question has estimand, observables, provenance/admissibility, falsification test, decision, action, learning consequence, and deferred limits.

REACQUIRE AUTHORITY
Refresh GitHub first. Read:
- QUANT_NORTH_STAR.md
- handoff/BLUE_PROJECT_REACQUISITION_2026-09-21.md
- handoff/BLUE_NEW_CONVERSATION_RESUME_PROMPT_2026-09-21.md
- handoff/BLUE_RESEARCH_FROZEN_EFFECT_ESTIMATE_PRESTAGE_RECEPTION_2026-09-21.md
- governance/BLUE_POST_P0_VERTICAL_PREBIGBUILD_CORRECTION_SPEC_2026-09-21.md
- NEXT_BUILD_MISSION.md

Also check whether a newer scientific-estimator specification mission/delivery has appeared. If it exists, read it and incorporate it. Do not duplicate or replace it.

BOUNDARY
Do not modify src/, tests/, scripts/, schemas, workflows, P0 runtime, target host, or capital state.
Do not implement code.
Do not invent profitable alpha.
Do not replace the scientific-estimator owner.
Only write the final handoff.

CORE OBJECTIVE
Define the economic questions Quant must answer across:
Forward -> Research -> Economic -> SIZE -> RISK -> FILLS -> BOOK -> Learning

For every question define:
1. plain-language question;
2. formal estimand/state;
3. exact observables needed;
4. PIT/provenance/admissibility conditions;
5. falsification test;
6. decision interpretation;
7. allowed action among CONTINUE, NO_TRADE, KILL, SCALE_DOWN, SHADOW, RETIRE, RESEARCH_MORE;
8. persisted evidence/state;
9. Learning consequence;
10. staleness/invalidity condition.

REQUIRED QUESTION FAMILIES

Q1 — Does the effect exist?
Does the declared Form-4 population have a positive allocation-weighted gross SPY-excess effect on the frozen coordinate?
Require delta_hat, interval, confidence, event count, coordinate binding, provenance.
Do not substitute net portfolio return, Sharpe or t-statistics.

Q2 — Is the evidence valid?
Is the estimate PIT-safe, correctly clustered, non-leaking, non-survivorship-biased, with valid missing-outcome and sample-use accounting?
Output: VALID_EVIDENCE | INVALID_EVIDENCE | INSUFFICIENT_EVIDENCE.

Q3 — Is it developmental or forward-confirmed?
Define exact conditions for DEVELOPMENT vs FORWARD_CONFIRMATION.
No automatic promotion merely because ForwardObservation exists.

Q4 — Does the effect survive real frictions?
Include spread, commission, impact, participation and any other modeled cost.
Require pre-sizing cost-model compatibility with the authoritative ExecutionModel and post-sizing/pre-fill implied-participation recheck.
Output: ECONOMIC_CONTINUE | NO_TRADE_COSTS | MODEL_INCOMPATIBLE.

Q5 — How large is economically justified?
Use Economic MarginSizingRule, then lifecycle cap.
Do not create a second sizing authority.

Q6 — Does the opportunity improve the current portfolio?
Use current Book exposures, concentration/correlation and overlap.
Output: approve, scale down, or veto.

Q7 — Is TRADE superior to NO_TRADE?
Given effect, uncertainty, frictions, size, capacity and Risk, is expected future wealth better with action than no action?
Require explicit NO_TRADE reason codes.

Q8 — Did execution preserve the expected edge?
Compare expected vs modeled shadow fill, spread/slippage/impact, capacity truncation and delay.
Output: EDGE_PRESERVED | EDGE_DEGRADED | EDGE_ERASED_BY_EXECUTION.

Q9 — Did the decision increase wealth?
Measure net wealth contribution in the persistent Book after modeled frictions.
Do not confuse market drift with discovered alpha.

Q10 — Is the edge persistent or decaying?
Across repeated independent evidence and shadow decisions, assess estimate stability, economic margin, execution quality and realized contribution.
Output: STABLE | DECAYING | BROKEN | INSUFFICIENT_HISTORY.

Q11 — Was a rejection correct?
For NO_TRADE/vetoed opportunities, define how later outcome analysis may classify correct rejection vs false reject without contaminating original prospective state.

Q12 — Where should Research search next?
Use accepted/rejected hypotheses, false positives/negatives, missed opportunity and execution shortfall to prioritize future Research. Do not claim guaranteed alpha.

TIME-HORIZON CLASSIFICATION
For every question classify one of:
IMMEDIATE_AFTER_BUILD
AFTER_FIRST_SHADOW_DECISION
AFTER_REPEATED_FORWARD_SAMPLE
ONLY_AFTER_LIVE/REAL_EXECUTION
NOT_ANSWERABLE_IN_FIRST_SLICE

DECISION CARD
Design one canonical decision card for a candidate with at least:
hypothesis_id, research_ticket_id, sample_id, evidence_label, delta_coordinate_hash, delta_hat, lower, upper, confidence_level, event_count, economic_margin, cost_model_identity, pre_size_cost_consistency, economic_size, lifecycle_cap, final_pre_risk_size, risk_verdict, risk_adjusted_size, execution_model_identity, post_size_participation, post_size_cost_consistency, action, reason_codes, expected_wealth_delta, book_operation_id, learning_outcome_id.
Flag unsupported items as FUTURE_FIELD instead of pretending they already exist.

FALSIFICATION MATRIX
For every question family include at least one false-positive and one false-negative failure mode, plus detection signal, affected authority and correct system response.

PRIORITIZATION
Produce a strict first-slice ordering using:
1. ability to kill false economic positives;
2. closeness to the North Star wealth objective;
3. ability to support a real decision;
4. dependency order.

Classify each question as:
MUST_ANSWER_IN_FIRST_BIG_BUILD
MUST_PERSIST_FOR_LATER_LEARNING
DEFER_UNTIL_REPEATED_FORWARD_EVIDENCE
DEFER_UNTIL_LIVE_EXECUTION.

SCIENCE BLOCKER
Explicitly state which questions cannot be answered while SCIENCE_EFFECT_ESTIMATE_CONTRACT = BLOCKED_MISSING_SCIENTIFIC_ESTIMATOR.
If a newer scientific spec closes it, update the map accordingly.

ONE BIG BUILD IMPACT
Define the minimum capabilities the eventual ONE BIG BUILD must provide so first-slice questions are answerable.
Capability examples: lawful EffectEstimate or fail-closed, DEVELOPMENT vs FORWARD_CONFIRMATION, Economic margin under compatible costs, sizing, independent Risk veto, one shadow fill, persistent Book mutation, durable NO_TRADE/executed outcomes, replay safety, later expected-vs-realized comparison.
Do not write implementation code.

STOPPING RULE
Stop when question families, estimands, evidence, actions, time horizons, falsification matrix, science dependencies and build-capability acceptance are explicit.
No second round unless Blue identifies a concrete contradiction.

FINAL HANDOFF
Write exactly:
handoff/CLAUDE_ECONOMIC_QUESTION_FALSIFICATION_MAP_2026-09-21.md

Final status:
ECONOMIC_QUESTION_MAP = READY_FOR_BLUE_REVIEW
or one precise blocker.

Final summary must include:
ECONOMIC_PROGRESS =
REMAINING_BLOCKER =
EXIT_CONDITION =
FIRST_SLICE_MUST_ANSWER =
FIRST_SLICE_MUST_PERSIST =
FORWARD_EVIDENCE_LATER_QUESTIONS =
LIVE_EXECUTION_LATER_QUESTIONS =
SCIENCE_BLOCKER_IMPACT =
ONE_BIG_BUILD_CAPABILITY_REQUIREMENTS =
ECONOMIC_QUESTION_MAP =

Commit and push only the final handoff to the assigned branch.
Return control to Blue.