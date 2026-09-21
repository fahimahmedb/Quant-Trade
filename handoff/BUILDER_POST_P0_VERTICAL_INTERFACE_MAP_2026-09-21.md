# BUILDER — POST-P0 VERTICAL INTERFACE MAP — 2026-09-21

## 0. Mission disposition

Mission type: READ_ONLY_ANALYSIS + HANDOFF_ONLY.

No Product code, tests, scripts, schemas, workflow, production configuration, P0 runtime, target host, merge, or cherry-pick was modified by this mission.

Exact mission branch state before this handoff commit:

- branch: builder/post-p0-vertical-interface-map-2026-09-21
- MISSION_START_HEAD = c4ad15e505a3c3554571bf0d8bed345a455baaac
- PRE_HANDOFF_HEAD_VERIFIED = c4ad15e505a3c3554571bf0d8bed345a455baaac
- parent / Blue baseline = cbf30c1bb38dd69c11fb64c523c3aec694116b9c

A commit cannot truthfully embed its own final SHA. The containing commit of this file is therefore the delivery HEAD; Blue should resolve the branch ref after this handoff is pushed. The exact parent from which the handoff was written is pinned above.

Exact comparison authorities inspected:

- Forward = 83521dbfdd90027c90d04adfb7d814593c2355c5
- Economic = 35dff27b8fac53618da434ee6d31febbddcc0e69
- Blue / Research / Book = cbf30c1bb38dd69c11fb64c523c3aec694116b9c

At final pre-write verification, all three moving branch names still resolved identically to those pinned SHAs, and this Builder branch still resolved identically to c4ad15e505a3c3554571bf0d8bed345a455baaac.

Important ancestry fact: Forward and Economic are not descendants of current Blue. Comparing each pinned leaf with cbf30c1bb38dd69c11fb64c523c3aec694116b9c reports DIVERGED, with merge base 8d5dbb41559c4716e94d5290b6ae979a8b96143c. Therefore a whole-leaf merge/cherry-pick is not the correct unit of post-P0 integration.

## 1. Executive interface conclusion

FACT: the repository already contains most of the vertical mechanisms needed for the requested shadow loop, but they live on three semantic surfaces that are not yet joined:

SOURCE / FORWARD
→ ResearchTicket / StrategyDefinition
→ economic gate
→ sizing
→ Desk risk
→ Desk execution
→ persistent Ledger
→ LearningStore / StrategyRegistry.

FACT: canonical Forward already has an immutable, PIT-readable observation ledger. Blue already has a research factory, a persistent strategy lifecycle, a Desk with SCAN/VET/SIZE/RISK/FILLS/BOOK, a crash-safe DeskJournal, persistent Capital/Evaluation ledgers, and LearningStore. Economic V2 already has a cost/capacity/MEUE gate, durable assessment journal, margin-based sizing objects, and explicit research/execution consistency checks.

INFERENCE: the missing work is primarily boundary glue and authority ordering, not a new horizontal platform.

RECOMMENDATION: keep Blue cbf30c1... as the integration spine and selectively compose exact contracts from Forward 83521... and Economic 35dff...; do not merge either leaf wholesale.

The two highest-value unresolved seams are:

1. ResearchTicket / validated research → EffectEstimate on the exact frozen economic coordinate, without changing the scientific claim.
2. authority ordering around StrategyDefinition promotion to SHADOW and SIZE: Blue currently promotes validated research to SHADOW before quant.economics is consulted, while Economic V2 defines an independent economic gate and an economic-margin sizing rule.

These are Blue/science/economic decisions. They do not block this interface map.

## 2. Component / interface classification

Only the mission-authorized classifications are used below.

| Classification | Exact path | Exact source SHA | Function / class / schema | Vertical role | Justification |
|---|---|---|---|---|---|
| REUSE_AS_IS | src/quant/dataplane/forward_contracts.py | 83521dbfdd90027c90d04adfb7d814593c2355c5 | SourceProfile, SOURCE_INVENTORY | SOURCE authority/inventory | Already distinguishes authorized Yahoo capture, static sources, blocked providers and P0 exclusion without inventing availability. |
| REUSE_AS_IS | src/quant/dataplane/forward_capture.py | 83521dbfdd90027c90d04adfb7d814593c2355c5 | CaptureAttempt, ForwardCaptureRequest, execute_forward_capture | one source fetch → durable attempt + observations | The one-shot contract is already scheduler-independent and records success/failure lineage. |
| REUSE_AS_IS | src/quant/dataplane/forward_recorder.py | 83521dbfdd90027c90d04adfb7d814593c2355c5 | ForwardObservation, ForwardRecorder.as_of, session_seal, ledger_fingerprint | canonical forward record and PIT read surface | Append-only, immutable per key, conflict-visible and PIT-readable. This is the correct source object for Research, not a raw HTTP payload. |
| REUSE_AS_IS | src/quant/dataplane/forward_admissibility.py | 83521dbfdd90027c90d04adfb7d814593c2355c5 | forward_dataset_view, evaluate_forward_confirmation | decide whether forward data may carry FORWARD_CONFIRMATION | Prevents a fitted/validation-spent version from being laundered as independent confirmation. |
| DEFER | src/quant/dataplane/forward_coverage.py | 83521dbfdd90027c90d04adfb7d814593c2355c5 | ExpectedCalendar, ForwardCoverageLedger | operational completeness / missing-vs-unknown tracking | Correct and valuable, but not required to prove one-observation vertical plumbing. |
| DEFER | scripts/forward_capture_runner.py | 83521dbfdd90027c90d04adfb7d814593c2355c5 | run-once / status / coverage CLI | manual capture driver | Continuous scheduling is explicitly not part of the first vertical interface proof. Reuse one-shot capture only; do not create a second scheduler. |
| REUSE_AS_IS | src/autonomous_research/ticket.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | ResearchTicket | canonical durable research candidate/hypothesis envelope | Already carries ticket_id, instruments, observed_at, information_available_at, source_refs, hypothesis, validation_result, paper_decision, lesson and next_action_hint. |
| DEFER | src/autonomous_research/scanner.py; src/autonomous_research/pipeline.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | scan_lag_dependence, run_discovery_cycle | older bounded historical research slice | It consumes a historical close series/TSV and is not the current Blue Product research integration seam. Do not create a second Product pipeline around it. |
| DEFER | src/autonomous_research/orchestrator.py; src/autonomous_research/runtime.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | ResearchCampaign, PersistentQueue, ResearchTask | standalone research runtime | Useful restart primitives exist, but the Blue Control Plane already owns Product sequencing. No second scheduler/control plane is needed for the first slice. |
| ADAPT | src/quant/factory/workers.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | run_lane, _finish | current Blue research factory and strategy registration | This is the current Product research seam. It must accept a PIT forward-backed dataset/view and must stop treating research validation alone as sufficient for immediate SHADOW promotion. |
| REUSE_AS_IS | src/quant/factory/evaluate.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | walk_forward, summarize, falsify | scientific filtering/falsification | Already enforces causal open(t+1) timing, costs, beta attribution, multiple-testing and falsification. It is research evidence, not the economic gate. |
| ADAPT | src/quant/factory/strategies.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | StrategyDefinition, StrategyRegistry | durable strategy identity, versioning, SHADOW/DECAYING/RETIRED lifecycle | The store and transitions are reusable, but the transition into SHADOW must be downstream of the resolved VET/economic authority order. |
| MISSING_GLUE | no existing single path | N/A | ForwardObservation → Research input adapter | FORWARD → RESEARCH | No current Research entry point directly consumes ForwardObservation / ForwardRecorder.as_of while retaining its content address and timing provenance. |
| MISSING_GLUE | no existing single path | N/A | research VET boundary | RESEARCH → VET | Blue has research validation and an operational Desk VET, but no explicit pre-economic disposition that means “scientifically admissible for economic assessment, not yet tradable.” |
| CONFLICT / BLUE_DECISION_REQUIRED | src/quant/factory/workers.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | _finish, StrategyDefinition.transition | VET/economic authority ordering | A passed research result is currently moved VALIDATED → SHADOW before quant.economics is consulted. Economic V2 was explicitly built as a downstream gate. |
| ADAPT | src/quant/economics/decision.py | 35dff27b8fac53618da434ee6d31febbddcc0e69 | EffectEstimate, PortfolioInteraction, economic_gate, EconomicVerdict | ECONOMIC ASSESSMENT | Gate is reusable once inputs are semantically compatible. The adapter into EffectEstimate is not present and must not be guessed. |
| REUSE_AS_IS | src/quant/economics/journal.py | 35dff27b8fac53618da434ee6d31febbddcc0e69 | compute_input_fingerprint, AssessmentRecord, EconomicAssessmentJournal | durable economic decision before Desk | Already idempotent, restart-safe, conflict-detecting and explicitly tested for crash-after-assessment-before-Desk. |
| REUSE_AS_IS | src/quant/economics/recipe.py; src/quant/economics/frictions.py; src/quant/economics/value.py; src/quant/economics/states.py | 35dff27b8fac53618da434ee6d31febbddcc0e69 | MEUERecipe, KForwardRecipe, PhiInstance, economic state vocabulary | economic threshold/friction mechanics | Existing engine fails closed/provisional when authority is missing. No new economic engine is justified. |
| REUSE_AS_IS | src/quant/economics/capacity.py | 35dff27b8fac53618da434ee6d31febbddcc0e69 | CapacityLimit, apply_capacity, CapacityOutcome | economic capacity before portfolio risk | Missing liquidity is not treated as unlimited. Relative-weight-changing clipping becomes a new policy version. |
| REUSE_AS_IS | src/quant/economics/consistency.py | 35dff27b8fac53618da434ee6d31febbddcc0e69 | ExecutionCostModel, verify_research_cost_consistency | bind research cost assumption to executable participation | This is the existing guard for ECON-001 and must remain in the chain. |
| CONFLICT / BLUE_DECISION_REQUIRED | src/quant/economics/sizing.py | 35dff27b8fac53618da434ee6d31febbddcc0e69 | MarginSizingRule, SizingPlan, size_lane | economic-margin SIZE | Blue Desk currently sizes from lifecycle capital_fraction × strategy_allocation. Economic V2 sizes from economic margin. One authority/composition rule must be chosen before a positive-size fill path. |
| CONFLICT / BLUE_DECISION_REQUIRED | src/quant/desk/desk.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | CapitalDesk._run_strategy SIZE block | current Product SIZE | It is coherent with current V1 Desk but does not consume EconomicVerdict.margin_of_safety or capital_order_eligibility. |
| REUSE_AS_IS | src/quant/desk/risk.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | RiskLimits, evaluate, verify_final | independent portfolio RISK | It scores the actual Book, can throttle gross exposure, and re-checks the exact post-fill portfolio. Economic CONTINUE is therefore not an approved order. |
| REUSE_AS_IS | src/quant/desk/execution.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | ExecutionModel.fill | authoritative Blue shadow-fill simulator | It fills at next-session open, charges commission/spread/impact, capacity-truncates and emits implementation shortfall. A shadow-fill abstraction already exists. |
| CONFLICT / BLUE_DECISION_REQUIRED | src/quant/economics/opening.py | 35dff27b8fac53618da434ee6d31febbddcc0e69 | OpeningExecutionModel.fill | economic opening-regime model | It overlaps Blue ExecutionModel.fill. It should not become a second booking engine. Blue must define which model supplies economic assumptions and which produces actual shadow fills, and how their coefficients/provenance stay consistent. |
| ADAPT | src/quant/desk/opportunity.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | OpportunityTicket | downstream VET/SIZE/RISK/FILLS/BOOK trace | Existing stage_trace/detail can carry upstream research/economic identifiers without requiring a new top-level ticket family. The current operational VET remains distinct from research VET. |
| REUSE_AS_IS | src/quant/desk/journal.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | DeskJournal.begin, commit, pending_plan, decision_snapshot | durable intent before Book mutation / crash recovery | Exactly the needed write-ahead boundary for fills and NO_TRADE outcomes. |
| REUSE_AS_IS | src/quant/book/ledger.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | Ledger.apply_fill, mark_to_market, summary | PERSISTENT BOOK | Preserves one bankroll, per-strategy sleeves, cash, P&L, fees and deterministic idempotent mutations. |
| MISSING_GLUE | no existing single path | N/A | stable upstream-id binding carried into DeskJournal / Ledger operation_id | ECONOMIC → Desk → BOOK provenance | Book financial state is sufficient, but current operation_id only binds opportunity_id:symbol and OpportunityTicket has no canonical ResearchTicket/EconomicAssessment refs. Use linkage, not a second Book. |
| ADAPT | src/quant/learning/store.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | LearningStore.record_research, assess_rejections | LEARNING / MEMORY | Existing store already learns research lessons and false rejects. It needs one narrow ingestion of Desk/economic outcome references and execution quality for the vertical slice. |
| REUSE_AS_IS | src/quant/factory/strategies.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | lifecycle_history, previous_versions, retirement_reason | RESCAN / RETIRE / REPLACE persistence | Registry already preserves versions and retirement state. |
| DEFER | no existing automatic policy path | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | automatic DECAYING/RETIRED policy | automated rescan/retire/replace | No automatic decay/retirement policy was found in the inspected Blue control path. It is not required for the first one-ticket functional slice. |
| DEFER | src/quant/clock.py | cbf30c1bb38dd69c11fb64c523c3aec694116b9c | Control Plane tick/scheduling | autonomous continuous orchestration | The mission forbids runtime integration. First prove one deterministic vertical slice manually/in tests; schedule it only after Blue review. |
| DEFER | src/quant/operations/registry.py; scripts/economic_dashboard.py | 35dff27b8fac53618da434ee6d31febbddcc0e69 | EvidenceRegistry, economic dashboard | aggregate evidence observability | Useful after decisions exist; EconomicAssessmentJournal + existing ticket/journal/Book chain is sufficient for the first slice. Do not expand the slice for dashboard plumbing. |

## 3. Exact data-contract chain

### 3.1 SOURCE / FORWARD DATA

FACT: the canonical typed input is ForwardObservation in forward_recorder.py. Its durable accepted record is the row replayed by ForwardRecorder; Research should read it through ForwardRecorder.as_of(cutoff), not from the network adapter.

Core fields:

- symbol
- session_date
- fields
- source
- source_fingerprint
- recorded_at
- note
- market_session
- fetch_started_at
- fetch_completed_at
- source_timestamp
- source_timestamp_state
- content_address (derived)
- key (derived)

CaptureAttempt separately records attempt_id, source_id/source_version, requested symbols, fetch start/end, success/failure state, payload_hash, validation_state, lineage and sessions/symbols observed.

Answer to Q1: canonical Forward produces immutable ForwardObservation records in an append-only ForwardRecorder ledger, plus a CaptureAttempt audit record for the fetch.

### 3.2 FORWARD → RESEARCH

FACT: neither autonomous_research.run_discovery_cycle nor Blue factory.run_lane accepts ForwardObservation directly today.

Current research input shapes are:

- autonomous legacy slice: list of historical close values loaded from TSV;
- Blue Product factory: PricePanel loaded from a DatasetRegistry record.

Therefore the smallest adapter is not “ForwardObservation → strategy.” It is:

ForwardRecorder.as_of(decision_cutoff)
→ materialized PIT price-panel/view for the declared universe/session set
→ DatasetRegistry-compatible dataset/version identity
→ existing Blue run_lane / ResearchTicket.

The adapter must retain exact forward content addresses/ledger fingerprint in ResearchTicket.source_refs or candidate_data and must not rewrite recorded_at/source timestamps into a stronger time authority.

### 3.3 RESEARCH output

FACT: ResearchTicket already carries the required candidate/hypothesis envelope.

Blue factory.run_lane additionally produces a StrategyDefinition with:

- strategy_id/version/lane/spec
- hypothesis
- evidence
- dataset_id/fingerprint
- lifecycle + lifecycle_history
- shadow metrics
- evaluation_track
- previous_versions
- retirement_reason.

This strategy object is a durable downstream identity, but current automatic VALIDATED → SHADOW promotion is upstream of Economic V2 and therefore cannot remain an implicit authority decision after integration.

### 3.4 VET

There are two different existing notions and they must not be conflated:

1. Scientific research validation:
   factory.evaluate.falsify and ResearchTicket.validation_result.
2. Operational Desk VET:
   CapitalDesk._run_strategy checks next execution session, holding period, drift and no-trade band.

MISSING_GLUE: a narrow pre-economic VET interpretation between those two layers.

Recommended semantics, without a new subsystem:

- failed research validation → VET disposition NO_TRADE / REJECTED;
- passed research validation → VET disposition ELIGIBLE_FOR_ECONOMIC_ASSESSMENT;
- neither disposition grants SHADOW lifecycle or order authority.

The durable ResearchTicket remains the source evidence for that disposition.

### 3.5 VET → ECONOMIC ASSESSMENT

Economic V2 needs, at minimum:

EffectEstimate:
- delta_hat
- lower
- upper
- confidence_level
- evidence_label
- sample_provenance
- estimator_form = frozen allocation-weighted ratio
- clustering_unit_provenance
- optional event_count / p_value

MEUEResult:
- recipe_state
- BEEE
- margin
- MEUE
- recipe_hash/theta_hash

ThetaState:
- scenario identity
- modeled capital point
- geometry/allocation/execution policy ids
- expected deployed exposure Q and provenance
- permitted liquidity/participation
- evaluation regime

PortfolioInteraction:
- overlap_fraction
- residual_beta
- optional correlation_to_book
- capital_contention

Optional but important:
- CapacityOutcome
- ResearchExecutionConsistency.

FACT: current ResearchTicket / factory summary does not emit a D09-compatible EffectEstimate with lower/upper interval on that exact frozen coordinate.

UNKNOWN: no scientifically valid mapping from current net_return, Sharpe, correlation or t-statistic to EffectEstimate.delta_hat/lower/upper can be inferred from code structure.

Therefore ResearchTicket → EffectEstimate is MISSING_GLUE and may require a Blue/science decision. The adapter must fail closed rather than map a convenient existing metric onto the economic coordinate.

A validated ForwardObservation must also not be labeled EVIDENCE_FORWARD_CONFIRMATION merely because it was captured forward. That label is available only after evaluate_forward_confirmation admits the dataset/version under the UseLedger. Otherwise the economic evidence label remains development-only or the assessment fails closed.

### 3.6 ECONOMIC ASSESSMENT → SIZE

economic_gate returns EconomicVerdict:

- CONTINUE / NO_TRADE / KILL
- reason
- MEUE
- incremental effect interval
- net_expected_value
- margin_of_safety
- authority
- recipe_state
- capital_order_eligibility
- reasons
- full chain / violations.

EconomicAssessmentJournal can persist the exact decision before Desk receives it.

SIZE already exists in Economic V2 as MarginSizingRule + size_lane → SizingPlan.

However Blue Desk also has an independent current SIZE formula based on StrategyDefinition.capital_fraction and strategy_allocation.

No positive-size integration should silently apply both or choose one without Blue.

### 3.7 SIZE → RISK

FACT: RISK is independently represented by Blue desk.risk.

evaluate(ledger, strategy_id, target_notional, limits, prices) projects the real persistent Book, may scale the proposal, and returns approved/scaled_target/vetoes/checks.

verify_final rechecks the exact post-fill state because execution capacity truncation can change the portfolio after the first approval.

Economic CONTINUE is therefore only eligibility for portfolio consideration, never an approved order.

### 3.8 RISK → SHADOW FILL

Answer to Q10/Q11: a shadow-fill abstraction already exists; no new fill engine is needed.

Blue ExecutionModel.fill emits:

- symbol
- signed quantity
- reference_price
- fill_price
- commission
- slippage_bps
- impact_bps
- participation
- capacity_truncated
- notional
- signal_date
- execution_date
- implementation_shortfall.

This is sufficient as the minimum fill object for Book and Learning.

Economic OpeningExecutionModel is a modelling surface, not a reason to create a second booking path.

### 3.9 SHADOW FILL → PERSISTENT BOOK

Exact state mutation:

DeskJournal.begin(opportunity_id, strategy_id, session_date, ticket, fills)
→ Ledger.apply_fill(symbol, quantity, fill_price, commission, execution_date, strategy_id, deterministic operation_id)
→ DeskJournal.commit(...)
→ Ledger.mark_to_market(...).

Ledger already preserves:

- persistent cash
- per-strategy/per-symbol sleeves
- aggregate positions
- realized P&L
- unrealized P&L
- fees
- NAV and peak NAV/history
- fill count
- strategy attribution
- idempotent applied operation IDs.

Answer to Q13: financial state preservation is already adequate. Full upstream provenance is not inline in Book today. It can be preserved without expanding Book by binding the deterministic Book operation_id to an OpportunityTicket/DeskJournal payload that contains ResearchTicket id + EconomicAssessment id + input fingerprint. That linkage is the missing glue.

### 3.10 BOOK → LEARNING / MEMORY → RESCAN / RETIRE / REPLACE

Blue LearningStore already supports:

- research lessons via record_research;
- lane priorities;
- decision-quality assessment;
- TRUE_REJECT / FALSE_REJECT / UNDETERMINED;
- counterfactual P&L from EVALUATION ledger;
- capability/build tasks.

StrategyRegistry already supports:

- versioned StrategyDefinition;
- lifecycle_history;
- previous_versions;
- DECAYING;
- RETIRED;
- retirement_reason.

For the vertical slice, Learning should consume one normalized outcome assembled from existing records, not a new learning service:

- accepted opportunity: OpportunityTicket status/stage_trace;
- reject: ResearchTicket.validation_result / OpportunityTicket terminal state;
- NO_TRADE: EconomicAssessmentRecord or Desk terminal status;
- fills: OpportunityTicket.fills + Book operation ids;
- misses: zero fill / below-minimum / missing data / Forward coverage state when available;
- slippage: fill.slippage_bps + implementation_shortfall;
- errors: ticket FAULT / CaptureAttempt failure / economic violations;
- decay: StrategyDefinition.shadow/lifecycle evidence once a governed rule exists;
- retirement: StrategyDefinition.lifecycle_history + retirement_reason.

MISSING_GLUE for the first slice: one narrow LearningStore ingestion method (or equivalent use of its existing persisted lesson shape) that records upstream ids, terminal disposition, fill/shortfall summary and Book operation references idempotently.

DEFER: automatic decay thresholds, retirement policy and replacement search policy.

## 4. Provenance / PIT propagation map

The following fields must survive each boundary.

| Boundary | Required provenance/PIT carried forward |
|---|---|
| Capture → Forward ledger | source, source_fingerprint, payload_hash/lineage, session_date, market_session, source_timestamp + state, fetch_started_at, fetch_completed_at, recorded_at, content_address |
| Forward ledger → Research | exact as_of cutoff, accepted content_address(s), ledger/dataset fingerprint, source refs, information_available_at rule, no time-authority upgrade |
| Research → VET | ResearchTicket.ticket_id, dataset fingerprint/version, source_refs, observed_at, information_available_at, hypothesis, validation_result |
| VET → Economic | same ticket id/version plus exact EffectEstimate.sample_provenance and evidence label; FORWARD_CONFIRMATION only with admissibility proof |
| Economic → SIZE/RISK | EconomicAssessment.assessment_id, input_fingerprint, recipe/effect versions, code/protocol hashes, portfolio_context_ref, verdict/eligibility/reasons |
| RISK → Fill | exact final target/scaled_target, Book decision snapshot reference, Risk verdict/checks, execution_date |
| Fill → Book | opportunity_id, strategy_id, deterministic operation_id, fill price/quantity/commission; DeskJournal retains complete fill plan |
| Book → Learning | opportunity/economic/research ids, Book operation ids, terminal status, P&L/fees where observable, slippage/shortfall, replay status |
| Learning → Rescan/Retire/Replace | StrategyDefinition id/version/lifecycle, lesson, decision-quality result, next_action, retirement_reason when governed |

FINDING: Forward recorded_at is explicitly TIME_AUTHORITY_UNATTESTED_LOCAL_CLOCK. The interface must preserve that label; it must not be presented as an externally attested public timestamp.

## 5. VET gap analysis

FACT: current research validation is strong but is not an explicit Product VET authority object.

FACT: current Desk VET is operational rebalance eligibility, not research admissibility.

FACT: current factory _finish can move a research-passed StrategyDefinition directly through VALIDATED → SHADOW.

CONFLICT / BLUE_DECISION_REQUIRED: after Economic V2 is introduced, “validated research” and “economic CONTINUE” are distinct authorities. Direct SHADOW promotion before economic assessment would bypass the economic chain.

RECOMMENDATION: keep research falsification as the scientific VET evidence, add only a boundary disposition that means ELIGIBLE_FOR_ECONOMIC_ASSESSMENT, and move SHADOW eligibility downstream of the economic decision. Do not rename the Desk rebalance check; retain it as an operational VET later in the session.

## 6. Economic / friction / sizing / risk map

### Frictions

Economic V2 closed inventory:

- F1_EXPLICIT_FEES
- F2_OPEN_ENTRY_CROSSING
- F3_OPEN_ENTRY_SLIPPAGE
- F4_MARKET_IMPACT
- F5_EXIT_EXECUTION
- F6_FINANCING_BORROW
- F7_RESIDUAL_CAPITAL_DRAG.

KForwardRecipe requires every class to be modelled or explicitly authorized zero. CostComponent also declares shape and provenance.

Blue actual shadow fill currently applies:
- commission;
- half-spread;
- participation-dependent impact;
- capacity truncation;
- implementation shortfall.

Financing/borrow and residual capital drag exist in Economic V2 as economic cost classes but are not separate booked charges in Blue ExecutionModel.fill / Ledger.apply_fill today.

RECOMMENDATION: for the first slice, do not fabricate financing/borrow charges. A positive-size lane can proceed only under a recipe that explicitly models or authorizes zero according to existing Economic rules.

### Capacity

There are two capacity moments:

1. economic capacity: apply_capacity before economic/sizing decision;
2. execution capacity: ExecutionModel.fill can truncate actual fill.

These are not interchangeable. If execution truncation changes the final portfolio, Blue desk.risk.verify_final already rechecks it.

### ECON-001

FINDING, already reproduced by Economic V2 tests:

- Research factory cost assumption = 5.0 bps one way.
- Blue ExecutionModel at max_participation 5% models 11.5 bps one way.
- understatement = 6.5 bps.
- implied participation ceiling consistent with the 5 bps research assumption ≈ 0.006125 (0.6125%), far below 5%.

Economic V2 already has verify_research_cost_consistency and fails the economic path closed when inconsistent.

Do not change either constant in this mission.

## 7. Shadow-fill gap analysis

There is no missing core fill abstraction.

Blue ExecutionModel.fill is the appropriate shadow execution primitive because it is already the one CapitalDesk books and because Risk.verify_final composes with its actual fills.

The gap is lineage, not fill mechanics:

ResearchTicket
→ EconomicAssessment
→ OpportunityTicket
→ fill
→ Book operation.

OpportunityTicket.stage_trace/detail can carry these refs without inventing another top-level transaction model.

CONFLICT / BLUE_DECISION_REQUIRED: Economic OpeningExecutionModel and Blue ExecutionModel overlap in spread/impact/capacity modelling. Blue should define Economic OpeningExecutionModel as expected-cost/economic-model input and Blue ExecutionModel as actual shadow fill authority, or choose another explicit relationship. They must not silently drift.

## 8. Book transition map

Positive-fill path:

1. capture a close-time decision Book snapshot in DeskJournal.begin_session;
2. RISK evaluates against that immutable decision snapshot;
3. model fills at next open;
4. RISK.verify_final checks exact executed portfolio and commission-adjusted NAV;
5. DeskJournal.begin durably records intent before money moves;
6. Ledger.apply_fill mutates the correct sleeve using deterministic operation id;
7. OpportunityTicket completes BOOK stage;
8. DeskJournal.commit records terminal outcome;
9. Ledger.mark_to_market records the execution-session Book point.

NO_TRADE path:

1. terminal disposition is persisted in Research/Economic/Opportunity evidence;
2. no Ledger.apply_fill operation is created;
3. the session Book may still be marked forward with mark_to_market;
4. Learning receives the NO_TRADE reason and the unchanged Book reference.

This satisfies the North-Star property that NO_TRADE is a real decision, not a missing record.

## 9. Learning / Memory feedback map

REUSE:
- ResearchTicket/research memory for scientific lesson.
- LearningStore.record_research for Product lesson/priorities.
- Evaluation ledger + LearningStore.assess_rejections for false-reject measurement.
- StrategyRegistry for persistent lifecycle/version/retirement history.

ADAPT:
- ingest one vertical outcome record/reference set after Desk/Economic terminal state.

Minimum fields for that feedback event:

- research_ticket_id
- strategy_id/version if created
- economic_assessment_id/input_fingerprint if reached
- opportunity_id if reached
- terminal disposition + reason codes
- Book authority (CAPITAL or EVALUATION; never real-capital semantics)
- Book operation ids
- fill count
- commission
- slippage_bps / implementation_shortfall summary
- capacity_truncated flag
- risk vetoes
- failure/miss state
- next_action_hint.

No new generalized memory database is justified.

## 10. Conflict / duplication register

### C1 — whole-leaf integration unit

FACT: Forward and Economic leaves both diverge from Blue at merge base 8d5dbb4....

RISK: whole branch merge imports unrelated Wave 1/science/operations surfaces and creates an unnecessarily large conflict domain.

Disposition: do not merge/cherry-pick leaves; integrate exact selected contracts.

### C2 — research validation versus economic authority

FACT: factory workers can promote VALIDATED → SHADOW before economic_gate.

Disposition: CONFLICT / BLUE_DECISION_REQUIRED.

### C3 — ResearchTicket.paper_decision semantics

FACT: autonomous pipeline may emit PAPER_ACCEPT/NO_TRADE while Blue factory uses validation/lifecycle differently.

Risk: PAPER_ACCEPT can be mistaken for an economic/order authority.

Disposition: DEFER autonomous pipeline as Product seam; Blue ResearchTicket validation may only mean eligible for the next gate.

### C4 — Research → EffectEstimate

FACT: no exact compatible conversion exists.

Risk: mapping net_return/Sharpe/correlation onto the frozen delta coordinate would change the scientific claim.

Disposition: MISSING_GLUE + Blue/science decision. Fail closed until resolved.

### C5 — two SIZE rules

FACT:
- Blue Desk SIZE = decision NAV × lifecycle capital_fraction × strategy_allocation × weights.
- Economic V2 SIZE = MarginSizingRule(margin_of_safety) × modeled capital × weights.

Disposition: CONFLICT / BLUE_DECISION_REQUIRED before any positive-size integrated slice.

### C6 — economic versus actual execution model

FACT: OpeningExecutionModel and ExecutionModel overlap; ECON-001 proves current research/execution assumptions can diverge materially.

Disposition: CONFLICT / BLUE_DECISION_REQUIRED; retain ResearchExecutionConsistency guard.

### C7 — economic capacity versus fill truncation

FACT: economic capacity clipping can change policy identity; actual fill capacity may truncate again.

Disposition: both may remain, but final actual state must pass Risk.verify_final and any relative-weight change with scientific consequence must not be hidden.

### C8 — ResearchTicket versus OpportunityTicket

INFERENCE: these are not true duplicates if scopes remain strict:
- ResearchTicket = scientific candidate/evidence.
- OpportunityTicket = one dated Desk decision/execution trace.

Disposition: ADAPT by stable references; do not unify schemas.

### C9 — EconomicAssessmentJournal versus DeskJournal versus Ledger

INFERENCE: these are complementary:
- assessment decision;
- transaction intent/outcome;
- financial state.

Disposition: REUSE_AS_IS with stable ids linking them.

## 11. Minimum missing glue for one vertical slice

The smallest set is five narrow seams.

### G1 — Forward → Research adapter

Input: accepted ForwardRecorder.as_of rows and exact cutoff.
Output: a PIT PricePanel/DatasetRegistry-compatible view plus source refs/fingerprint for ResearchTicket.

Must not:
- read future observations;
- coerce missing fields to zero;
- upgrade local clock authority;
- infer FORWARD_CONFIRMATION.

### G2 — explicit research VET disposition

Input: ResearchTicket.validation_result + hypothesis/provenance.
Output: REJECT/NO_TRADE or ELIGIBLE_FOR_ECONOMIC_ASSESSMENT.

Do not create SHADOW authority here.

### G3 — Research → Economic effect adapter / fail-closed boundary

Input: VET-passed ResearchTicket.
Output:
- a semantically valid EffectEstimate on the frozen coordinate, only if such fields are explicitly produced under a governed scientific rule; OR
- an economic NO_TRADE/not-evaluable assessment with reason EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE.

This is the most important semantic guard.

### G4 — stable decision-id lineage into Desk

Carry ResearchTicket id + EconomicAssessment id/fingerprint into OpportunityTicket.stage_trace/detail and derive/retain deterministic Book operation ids through DeskJournal.

No Book schema expansion is needed for the first slice.

### G5 — terminal outcome → LearningStore

Record one idempotent lesson/outcome tying the above ids to NO_TRADE or fill/Book result, including slippage/shortfall/errors when present.

Everything else is existing machinery or deferred.

## 12. Proposed first vertical slice

RECOMMENDATION: make the first integration slice deliberately fail-closed-capable and accept NO_TRADE as the expected successful terminal outcome.

Functional proof:

1. SOURCE: take exactly one accepted ForwardObservation from ForwardRecorder.as_of(cutoff), with source/content/timing provenance.
2. RESEARCH: adapt the PIT data into the existing Blue research input shape and persist exactly one ResearchTicket.
3. CLAIM: the ticket contains one explicit hypothesis already in the ResearchTicket.hypothesis shape.
4. VET: derive one explicit pre-economic disposition from the existing validation result.
5. ECONOMIC:
   - if the ticket supplies a governed EffectEstimate on the frozen economic coordinate, run economic_gate and record it in EconomicAssessmentJournal;
   - otherwise record fail-closed economic NO_TRADE/not-evaluable, explicitly because the coordinate-compatible effect is unavailable. Do not synthesize a delta.
6. SIZE:
   - for NO_TRADE: target size = zero as a terminal consequence; no sizing-authority conflict needs to be resolved;
   - for a future CONTINUE path: stop until Blue resolves C5.
7. RISK: evaluate the zero target/no-op state or, only after C5 resolution, score the final positive target through desk.risk.
8. FILL:
   - NO_TRADE path produces no fill and records that as the terminal successful outcome;
   - positive-size path, once authorized, uses Blue ExecutionModel.fill only.
9. BOOK:
   - persist the dated Book mark / unchanged state for NO_TRADE;
   - for a fill path use DeskJournal.begin → Ledger.apply_fill → commit → mark.
10. LEARNING: record one LearningStore outcome with all stable ids and terminal reason.

Acceptance criteria:

- exactly one source observation is traceable end to end;
- no future Forward row is visible to Research;
- no evidence label is upgraded without admissibility;
- research validation does not by itself grant SHADOW/order authority;
- an incompatible scientific claim terminates as explicit NO_TRADE, not as an invented effect;
- economic assessment is durable before Desk;
- RISK remains independent;
- Book is not mutated by a NO_TRADE fill operation;
- one Learning record exists and references the same decision chain;
- restart/replay does not duplicate the economic assessment, Desk outcome or Book operation.

This proves interface integrity. It proves neither alpha nor profitability.

## 13. Proposed implementation order after Blue review

1. Blue decision checkpoint: C2 research→SHADOW ordering, C4 Research→EffectEstimate scientific contract, C5 SIZE authority, C6 execution/economic-model relationship.
2. Establish Blue baseline cbf30c1... as the integration spine; import only the exact required Forward and Economic contracts, not the leaf histories.
3. Implement/test G1 Forward→Research PIT adapter.
4. Implement/test G2 VET disposition and block direct research→SHADOW promotion.
5. Implement/test G3 fail-closed Research→Economic adapter plus EconomicAssessmentJournal persistence.
6. Implement/test the NO_TRADE first vertical slice through zero SIZE/RISK, unchanged Book mark and LearningStore.
7. Only after C5/C6 are explicitly resolved, enable the CONTINUE branch into positive economic SIZE → desk.risk → Blue ExecutionModel.fill → DeskJournal → Ledger.
8. Add one end-to-end restart/replay test with deterministic ids.
9. Only after the functional slice is green, consider Control Plane scheduling/status/UI exposure.

## 14. Work explicitly DEFERRED

- continuous Forward scheduling;
- Clock/Control Plane integration;
- target-host/systemd/cron work;
- P0 runtime or Gate-B changes;
- real capital;
- automatic alpha/profit claims;
- generalized event bus / workflow framework;
- new Book architecture;
- new scheduler;
- new Learning database;
- dashboards/UI polish;
- ForwardCoverageLedger operational completeness in the first slice;
- autonomous ResearchCampaign as a second Product runtime;
- automatic DECAYING/RETIRED thresholds;
- automated replacement search;
- sector/factor risk limits not already present in Blue;
- turnover-budget architecture not already present;
- calibration of financing/borrow or other unresolved economic parameters;
- changing RESEARCH_ONE_WAY_COST_BPS or ExecutionModel.max_participation;
- declaring t0;
- scientific protocol changes.

## 15. Blue decisions required

### B1 — scientific promotion order

Should a research-passed candidate remain VALIDATED / eligible-for-economic-assessment until Economic V2 returns the required disposition, rather than being moved directly to SHADOW?

Builder recommendation: yes; research validation and economic viability are different gates. Blue owns the decision.

### B2 — ResearchTicket → EffectEstimate contract

Which exact governed research estimator supplies delta_hat/lower/upper on the frozen allocation-weighted economic coordinate?

Builder cannot infer this from current backtest metrics. Until specified, the integrated path must terminate fail-closed as NO_TRADE/not-evaluable.

### B3 — SIZE authority

When Economic V2 returns CONTINUE, is MarginSizingRule/size_lane authoritative, is Blue lifecycle sizing an outer cap, or is another explicit composition intended?

Builder does not choose between them.

### B4 — economic execution model versus actual shadow fill

Define the authority relationship between Economic OpeningExecutionModel / KForward assumptions and Blue ExecutionModel.fill. Keep verify_research_cost_consistency mandatory.

### B5 — ECON-001 underlying parameter decision

Whether to raise research cost assumptions, lower executable participation, or otherwise resolve the inconsistency remains Blue/science authority. This map does not alter constants.

### B6 — lifecycle decay/retirement policy

StrategyRegistry has the states but no inspected automatic policy transitions them. Define later; not needed for the first slice.

## 16. Direct answers to mission questions

1. Canonical Forward record: accepted ForwardObservation in ForwardRecorder, with CaptureAttempt as fetch audit context.
2. Provenance/PIT: source, source_fingerprint, content_address, session/market session, source timestamp/state, fetch start/end, recorded_at + explicit unattested-local-clock authority, payload/lineage in CaptureAttempt.
3. Research input today: historical close series in autonomous pipeline or DatasetRegistry-backed PricePanel in Blue factory; no direct ForwardObservation consumer.
4. Research output today: ResearchTicket; Blue factory may also persist StrategyDefinition.
5. Real VET gap: no explicit pre-economic research disposition distinct from Desk rebalance VET and no authority ordering preventing research-only SHADOW promotion.
6. Economic fields: EffectEstimate + MEUEResult + ThetaState + PortfolioInteraction, with optional CapacityOutcome and ResearchExecutionConsistency.
7. Fees/spread/slippage/financing/capacity: Economic KForward models F1–F7; Blue actual fill charges commission/spread/impact and truncates capacity; financing/borrow are not separately booked by Blue fill today.
8. SIZE exists: Economic MarginSizingRule/SizingPlan/size_lane; Blue Desk also has a competing current sizing rule.
9. RISK exists independently: desk.risk.evaluate + verify_final.
10. Shadow fill exists: desk.execution.ExecutionModel.fill.
11. Minimum fill object: existing fill dictionary is already sufficient; missing piece is upstream lineage.
12. Book API: DeskJournal.begin → Ledger.apply_fill → DeskJournal.commit → Ledger.mark_to_market.
13. Book financial state: yes; end-to-end provenance requires linkage through DeskJournal/opportunity ids, not a new Book.
14. Learning: LearningStore + Evaluation ledger + StrategyRegistry cover research lessons and false rejects; adapt one terminal outcome ingestion for fills/misses/slippage/errors and defer governed decay/retire automation.
15. Conflicts: leaf divergence, direct research→SHADOW promotion, Research→EffectEstimate absence, two SIZE rules, two execution/cost model surfaces, capacity at economic and actual-fill layers, ResearchTicket/OpportunityTicket scope overlap.
16. Smallest coherent baseline: Blue cbf30c1... as spine, selectively composed with exact Forward 83521... contracts and Economic 35dff... contracts. No whole-leaf merge.
17. Exact missing glue: G1–G5 above.

## 17. Boundary attestation

P0 runtime = untouched
PRODUCT_INTEGRATION = PAUSED
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE

No alpha claim was made.
No profitability claim was made.
No Product implementation was performed.
No source/test/script/schema/workflow file was modified.
No Forward/Economic leaf was merged or cherry-picked.

PRODUCT_PRESTAGE_INTERFACE_MAP = READY_FOR_BLUE_REVIEW
