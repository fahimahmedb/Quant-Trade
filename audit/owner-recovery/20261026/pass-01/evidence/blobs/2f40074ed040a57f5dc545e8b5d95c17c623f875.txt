# CHECKPOINT 015 — V2 Edge-Discovery Improvement Specification

Recorded 2026-10-20 (Europe/Paris).

## Status

`CP15_V2_EDGE_DISCOVERY_IMPROVEMENT_SPEC = CURRENT`

This checkpoint does not supersede CP12–CP14. It adds a forward-looking V2 improvement specification derived from the current Research OS implementation and the economic-history review.

Observed V2 HEAD before CP15:

`1f3c0a28147370190d4ca8f09933497d67e28bec`

Observed message:

`Research OS legacy_duplicate_check FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-009-g1-5d3e3c03e437 [skip ci]`

Observed audit branch HEAD before CP15:

`da37826e85884f0c91bee1d6ebf1b24c895c4186`

All four hard authorities remain CLOSED:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

---

## 1. Clarification: Event/Documents and related families are already native V2

Fresh inspection of `research/research_os/worker_stages.py` and `research/research_os/engines/builtin.py` shows that the canonical V2 producer surface already includes:

- `QUANT_MECHANISM`
- `FUNDAMENTAL_RESEARCH`
- `EVENT_DOCUMENT`
- `INSTITUTIONAL_FLOW`

with engine registry keys:

- `quant`
- `fundamental`
- `event_document`
- `institutional_flow`

These are not independent projects outside V2.

They pass through the canonical V2 producer flow:

`legacy_duplicate_check -> research -> disconfirmation -> freeze_hypothesis -> validation_handoff`

and then the canonical independent challenge / Red Team / integration / portfolio-readiness stack.

Therefore:

`EVENT_DOCUMENT_IS_NATIVE_V2 = TRUE`

`INSTITUTIONAL_FLOW_IS_NATIVE_V2 = TRUE`

`FUNDAMENTAL_IS_NATIVE_V2 = TRUE`

`QUANT_MECHANISM_IS_NATIVE_V2 = TRUE`

No separate Event/Documents architecture should be created.

---

## 2. Why the prior Codex work did not exhaust V2 improvement

The economic-readiness Builder missions were primarily horizontal readiness work: frozen experiment protocol, independent validation/Red Team, portfolio/economic identity and producer evidence depth.

They were not a declaration that all producer families had reached final research depth.

Builder 5 already treated Institutional/Forced Flows, Event/Documents, Quant/Mechanisms and Fundamental as priority producer engines.

The remaining improvement opportunity is therefore not family creation but **producer-depth, mechanism quality, source breadth, ranking quality and observability**.

---

## 3. Current producer-engine maturity

The current V2 engine registry is real and operational, but the built-in engines remain `v0` research producers.

Current documentary support is intentionally narrow. Examples include:

- qualified Apple FY2025 statement cells for Fundamental;
- Apple dividend announcement comparison for Event/Document;
- SEC T+1 settlement rule / explanatory material for Institutional Flow.

The current engine dossier itself truthfully records important unknowns. Examples:

- Event/Document may identify a change in declared distribution or guidance while payer, expectations, consensus surprise and market response remain unqualified;
- Institutional Flow may identify a settlement constraint while actual transaction eligibility, quantity, funding pressure and directional flow remain UNKNOWN;
- Fundamental may establish accounting facts while market pricing remains untested.

This is scientifically correct, but it means V2 currently has stronger **research process quality** than **economic-mechanism depth**.

---

## 4. V2-forward objective

Do not add a V3 and do not create new top-level producer architecture.

Target improvement:

`V2 PRODUCER DEPTH -> ECONOMIC MECHANISM COMPLETENESS -> BETTER FRONTIER PRIORITISATION -> CLEANER FUTURE ECONOMIC TEST CANDIDATES`

The future Research OS should preferentially generate candidates where the system can answer, before seeing outcomes:

1. Who can economically pay?
2. Why is that actor constrained, slow, mandated or structurally disadvantaged?
3. What exact mechanism transfers value?
4. What instrument expresses the thesis?
5. What clock/window governs the mechanism?
6. What universe is eligible?
7. What capacity bottleneck exists?
8. What implementation/cost structure would consume the edge?
9. What evidence could falsify the mechanism before outcome access?
10. What makes the candidate genuinely distinct from already tested exposure?

Unknowns remain allowed, but economically critical unknowns must restrict readiness and priority rather than be silently ignored.

---

## 5. SPEC A — Economic Mechanism Completeness Contract

Extend the canonical candidate/dossier representation so every producer family declares, where applicable:

- `payer`
- `constrained_actor`
- `constraint_type`
- `constraint_binding_evidence`
- `counterparty_or_beneficiary`
- `economic_transfer_mechanism`
- `instrument`
- `universe`
- `timing_clock`
- `horizon`
- `directionality_basis`
- `capacity_bottleneck`
- `cost_structure`
- `event_or_rule_dependency`
- `source_identity`
- `implementation_dependency`
- `mechanism_falsifiers`
- `economic_unknowns`

Do not fabricate missing fields. Use explicit `UNKNOWN` states.

Critical unknowns must propagate into readiness/reason codes.

---

## 6. SPEC B — Evidence Ladder for Forced / Institutional Flows

Institutional Flow should distinguish at least these levels:

`RULE_EXISTS`

`ACTOR_IN_SCOPE`

`CONSTRAINT_APPLIES`

`BINDING_PRESSURE_EVIDENCED`

`DIRECTIONAL_FLOW_EVIDENCED`

`TRADABLE_INSTRUMENT_MAPPED`

`CLOCK_IDENTIFIED`

`CAPACITY_DECLARED`

`COST_MODEL_DECLARED`

A rule or settlement deadline alone must never be promoted into a forced-buy/forced-sell claim.

Priority should rise only as the economic chain becomes more complete.

---

## 7. SPEC C — Event/Documents depth

Event/Documents is already native V2. Improve it rather than creating a parallel project.

Target source/mechanism classes should include, where primary-source capture and PIT semantics can be qualified:

- guidance revisions;
- declared distributions / buybacks / capital-return changes;
- corporate actions;
- index/provider implementation notices where legally and technically accessible;
- issuance/redemption/auction/event calendars;
- official regulatory/issuer documents that create a known implementation clock;
- other primary-source events with a falsifiable expectation-transfer mechanism.

For every Event candidate distinguish:

`DOCUMENT_CHANGE`

from

`EXPECTATION_SURPRISE`

from

`FORCED_OR_DELAYED_REACTION_MECHANISM`

from

`ECONOMIC_PAYOFF`.

A document change alone is not an edge.

---

## 8. SPEC D — Fundamental depth

Fundamental candidates should separate accounting fact from re-rating thesis.

Require explicit distinction between:

- measured operating/accounting fact;
- valuation/expectation hypothesis;
- catalyst or clock;
- expected counterparty mistake/slow update;
- instrument/universe;
- implementation horizon;
- falsifier.

Do not treat good company fundamentals as edge by themselves.

---

## 9. SPEC E — Quant Mechanism discipline

Quant-family candidates should not be prioritized merely because a statistical shape exists.

Require either:

- an economically interpretable mechanism;
- a stable structural microstructure/flow explanation;
- or an explicitly classified empirical-only candidate with stronger multiplicity penalties and lower priority until mechanism evidence improves.

Historical V1 cross-sectional failures should remain active negative knowledge against mechanically regenerating similar high-turnover pressure/reversal families without a materially distinct mechanism.

---

## 10. SPEC F — Historical economic memory integration

CP12 remains responsible for historical reconciliation.

V2-forward should consume a normalized historical mechanism/result index, without contaminating active blinded epochs.

At minimum preserve distinctions among:

- `FINAL_NEGATIVE_RESULT`
- `POSITIVE_BUT_INSUFFICIENT_SIGNAL`
- `BLOCKED_DATA_PERMISSION`
- `FROZEN_UNEXECUTED`
- `PROTOCOL_INVALIDATED`
- `HISTORICAL_RESULT_WITH_LIMITATIONS`

Examples that must not be flattened together include:

- V1 cross-sectional / execution-aware failures after causal repair;
- F1 Stage-B sealed rejection;
- Box Office negative result;
- F2 blocked data permission;
- EURUSD frozen/unexecuted state;
- Weather/cross-domain evidence with explicit limitations.

A negative family must not be regenerated unless a candidate states a materially distinct mechanism or a valid revisit condition.

---

## 11. SPEC G — Cross-domain mechanism replication map

Where historical evidence suggests the same underlying mechanism may recur across different domains, maintain a structural replication map.

Do not convert cross-domain similarity into empirical correlation.

Record:

- shared mechanism identity;
- differing payer/actor;
- differing instrument/domain;
- clock differences;
- source identity;
- cost/capacity differences;
- protocol quality;
- result status;
- whether the replication is genuinely independent.

This should help distinguish one-off dataset accidents from recurring economic mechanisms.

---

## 12. SPEC H — Frontier prioritisation by economic information value

Improve scheduler/frontier reason codes without using outcomes.

Candidates should be prioritised using explicit pre-outcome dimensions such as:

- source qualification completeness;
- payer identification;
- binding constraint evidence;
- mechanism distinctness;
- clock precision;
- instrument mapping;
- capacity plausibility;
- cost-model availability;
- falsifiability;
- historical negative-memory conflict;
- expected information gain from the next research action.

Avoid opaque labels such as `HIGH_VALUE_CANDIDATE` unless decomposed into deterministic reason codes.

Do not rank using hidden or sealed economic outcomes.

---

## 13. SPEC I — Candidate maturity vector

Expose candidate state across separate axes rather than a single score:

- `SOURCE_MATURITY`
- `MECHANISM_MATURITY`
- `PAYER_CONSTRAINT_MATURITY`
- `IMPLEMENTABILITY_MATURITY`
- `SCIENTIFIC_VALIDATION_STATE`
- `PORTFOLIO_RELATION_STATE`
- `ECONOMIC_TEST_READINESS`
- `AUTHORITY_STATE`

Optional summary ranking may exist for scheduling, but the underlying axes and reason codes must remain visible.

No scalar score may masquerade as probability of profitability.

---

## 14. SPEC J — Economic Edge Board / owner observability

The Owner currently lacks a factual economic/research overview while the Site bridge is incomplete.

Create a durable factual projection that can later feed Live Lab.

It should show, by family:

- candidates generated;
- candidates duplicate-blocked;
- candidates disconfirmed;
- frozen hypotheses;
- validator PASS/BLOCK;
- Red Team PASS/BLOCK;
- shadow-readiness state;
- current missing evidence;
- historical result classification;
- latest action/reason code;
- source identity;
- mechanism/payer/clock summary;
- `ECONOMIC_RESULT = NOT_OBSERVED` for current pre-outcome candidates.

Historical economic metrics may be shown only when already admissible historical evidence and clearly labelled as historical, never as current V2 outcome access.

This board must be a projection of durable state, not a second state system.

---

## 15. SPEC K — Future authorized economic-test package

Without opening the membrane now, every candidate that reaches readiness should be able to produce a complete immutable future-test package containing at least:

- hypothesis/generation identity;
- source snapshot hashes;
- source/model PIT metadata;
- universe;
- clock;
- instrument/expression;
- cost model;
- capacity declaration;
- multiplicity/trial accounting;
- power/MDE where applicable;
- frozen decision map;
- falsification criteria;
- protocol hash;
- candidate hash;
- validator/Red Team bindings;
- no-outcome-access proof.

This extends rather than replaces the existing economic-readiness Builder work.

---

## 16. SPEC L — Source breadth without source-truth confusion

Increase producer source breadth through qualified source packets/adapters, not direct model browsing treated as fact.

Preserve:

`PRIMARY_CAPTURE -> PROVENANCE -> PIT/AVAILABILITY -> STRUCTURED PACKET -> ENGINE`

Model reasoning may critique or propose falsifiers, but cannot invent documentary facts.

Each new adapter must have adversarial provenance/clock/revision tests.

---

## 17. Relationship to CP12 and Closure work

Do not implement CP15 by bypassing the Final Integrator/CP12 reconciliation.

CP12 may discover historical producer capabilities that already solve some of these gaps.

Therefore V2-forward execution order should be:

1. treat CP15 as target specification;
2. let CP12/Final Integrator classify historical equivalent capabilities;
3. import rather than rebuild where equivalent code/evidence exists;
4. build only residual gaps;
5. keep V2 autonomous writer safe;
6. do not open economic outcomes.

---

## 18. What is NOT required

CP15 does NOT require:

- a new research family;
- a V3;
- rebuilding Validator/Red Team;
- rebuilding portfolio identity;
- rebuilding Capital Desk/Book;
- opening economic experiment authority;
- prospective observation;
- real capital;
- live trading.

---

## 19. Acceptance criteria for the future V2 improvement package

The future implementation should prove that:

1. all four existing producer families remain canonical;
2. each candidate carries explicit economic-mechanism unknowns rather than silently omitting them;
3. payer/constraint/clock/instrument reasoning is structurally represented;
4. Event/Documents does not equate document change with edge;
5. Institutional Flow does not infer directional flow from rule existence alone;
6. Fundamental does not equate quality with re-rating edge;
7. Quant empirical-only candidates are clearly classified and penalized for weak mechanism support;
8. historical negative knowledge blocks trivial rediscovery;
9. frontier scheduling exposes deterministic reason codes;
10. owner observability can truthfully show the funnel without opening outcome access;
11. future economic-test packages are complete and immutable;
12. all four authority flags remain false.

---

## 20. Final interpretation

The newly identified V2 improvement is primarily a **research-quality and economic-mechanism-depth upgrade**, not a missing-family repair.

`V2_FAMILIES_EXIST = TRUE`

`V2_PRODUCER_DEPTH_IS_FINAL = FALSE`

`EVENT_DOCUMENT_REQUIRES_SEPARATE_ARCHITECTURE = FALSE`

`INSTITUTIONAL_FLOW_REQUIRES_SEPARATE_ARCHITECTURE = FALSE`

`CP15_TARGET = DEEPEN_EXISTING_V2_PRODUCERS_AND_OWNER_OBSERVABILITY`

`ECONOMIC_OUTCOME_ACCESS = CLOSED`

Resume marker:

`CP15_RESUME_POINT = V2_EDGE_DISCOVERY_DEPTH_SPEC_READY_FOR_CHALLENGE_AND_IMPLEMENTATION_AFTER_RECONCILIATION`
