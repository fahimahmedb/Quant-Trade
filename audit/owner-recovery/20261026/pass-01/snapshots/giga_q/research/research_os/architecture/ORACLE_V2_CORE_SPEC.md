# Oracle Research OS V2 Core — Canonical Implementation Specification

Status: OWNER-AUTHORIZED IMPLEMENTATION
Branch: `builder/oracle-v2-core-20261020`
Base: Oracle H24 V1 operationally qualified

## Claim boundary

V2 Core may prove only:

`AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED`

Strongest candidate-level status:

`READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY`

Neither status implies profitability, alpha, positive expectancy, portfolio usefulness or live-trading readiness.

## Authority boundary

The following remain closed throughout V2 Core:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

## Owner override

Prior P0-D server-side canonical-ref protection is lifted. GitHub branch protection/rulesets are not a V2 Core implementation or Definition-of-Done requirement.

Normal operating discipline still forbids force-push, rewind, reset and deletion of autonomous evidence. P0-D lift is not authorization for destructive Git operations.

## Architectural planes

1. Governance Plane — policies, authorities, epoch controls.
2. Orchestration Plane — queue, claims, leases, retries, recovery and routing.
3. Research Plane — ideation, evidence gathering, disconfirmation, archaeology and freeze.
4. Evidence Plane — claim/source/locator/time/hash/transformation binding.
5. Validation Plane — independent reconstruction and challenge.
6. Evaluation Plane — architecturally present but sealed in V2 Core.
7. Durable Scientific Archive — GitHub evidence, protocols, receipts and immutable research records.
8. Oversight/Learning Plane — research-side supervision, escalation and successor-epoch learning.

## Research Epoch

Every substantive research trial belongs to exactly one `research_epoch_id`.

The epoch manifest binds at minimum:

- `research_epoch_id`
- `parent_epoch_id`
- `opened_at`
- `knowledge_cutoff`
- `research_window`
- `export_cutoff`
- `close_policy`
- `close_policy_hash`
- `feedback_release_policy`
- `feedback_release_policy_hash`
- `research_policy_hash`
- `model_routing_policy_hash`
- `allowed_model_set`
- `allowed_model_change_policy`
- `source_policy_hash`
- `retrieval_policy_hash`
- `validator_policy_hash`
- `max_candidate_exports`
- `scheduled_close_at`
- `epoch_knowledge_parent`
- `epoch_feedback_dependencies`
- `contamination_status`
- `epoch_manifest_hash`

Before first Evaluation export the close policy must already be frozen. After first Evaluation export:

`CLOSE_POLICY_MUTATION = FORBIDDEN`

Allowed close-policy classes are `TIME_BOUND`, `N_EXPORTS` and `PREDECLARED_COMPOSITE`.

## Time model

Do not collapse:

`knowledge_cutoff != generation_time != export_time != evaluation_time != feedback_release_time`

## Leakage model

`SOURCE_PIT` and `MODEL_PIT` are separate.

Where model-weight hindsight cannot be proved absent, use:

`MODEL_PIT = NOT_PROVABLE`

and, for historical ideation:

`HISTORICAL_IDEA_GENERATION_NOT_PROVABLY_PIT`

Historical LLM reconstruction may qualify process discipline but not genuine historical discovery ability.

## Model routing

Use capability/risk routing:

- `R0_DETERMINISTIC`
- `R1_LOCAL_STANDARD`
- `R2_DIVERSE_REVIEW_REQUIRED`
- `R3_SENIOR_ESCALATION`

There is no silent hosted fallback.

Each trial binds exact model identity, prompt hash, context hash, retrieval-manifest hash and sampling parameters where controllable.

## Trial accounting

Trial accounting starts at ideation, not candidate freeze.

Every substantive attempt receives `research_trial_id` and records generated alternatives, discarded alternatives, retries and discard reasons.

`RESEARCH_GENERATION_TRIAL` and future `ECONOMIC_EVALUATION_TRIAL` are distinct concepts.

## Candidate schema

Universal CandidateCore:

- `hypothesis_id`
- `generation_id`
- `research_trial_id`
- `research_epoch_id`
- `family`
- `claim`
- `mechanism_statement`
- `universe`
- `clock`
- `horizon`
- `economic_expression`
- `evidence_manifest`
- `falsification_scope`
- `decision_map`
- `known_confounders`
- `disconfirmation_manifest`
- `producer_identity`
- `candidate_hash`

Exactly one primary family extension is required:

- `FundamentalExtension`
- `EventExtension`
- `ForcedFlowExtension`
- `QuantExtension`

Semantic nulls are distinct:

- `UNKNOWN`
- `NOT_APPLICABLE`
- `NOT_YET_MEASURABLE`
- `UNRESOLVED`

A family must not invent irrelevant causal fields merely to satisfy a global schema.

## Validator independence

Independence has four axes:

1. information isolation;
2. retrieval independence;
3. cognitive independence appropriate to gate risk;
4. state isolation.

Validator output records validator identity/version/model/prompt/context/retrieval hashes.

Execution state is separate from scientific decision.

Execution states include `PENDING`, `RUNNING`, `COMPLETE`, `RETRYABLE_ERROR`, `PERMANENT_ERROR`, `INTERRUPTED`.

Scientific decision, when defined, is only `PASS` or `BLOCK`.

Epistemic blockers are explicit machine-readable reasons such as `INSUFFICIENT_EVIDENCE`, `CONTRADICTORY_EVIDENCE`, `PIT_UNRESOLVED`, `MECHANISM_UNRESOLVED`, `IMPLEMENTABILITY_BLOCK`, `PROTOCOL_INVALID`, `MULTIPLICITY_UNRESOLVED`.

Infrastructure failure is not scientific falsification.

## Multidimensional status

Scientific maturity:

`IDEA | EVIDENCE_BOUND | DISCONFIRMATION_ATTEMPTED | FROZEN | VALIDATED`

Experiment readiness:

`INCOMPLETE | READY`

Portfolio relationship:

`UNKNOWN | DISTINCT | VARIANT | REPLICATION | DUPLICATE | COMPLEMENTARY`

Authority:

`CLOSED | OWNER_AUTHORIZED`

No dimension substitutes for another.

## Portfolio boundary

`STRUCTURAL_OVERLAP != EMPIRICAL_CORRELATION`

Without admissible evaluated returns:

- `empirical_correlation = UNKNOWN`
- `marginal_portfolio_contribution = NOT_ESTIMATED`

Portfolio relation informs interpretation and experiment selection; it does not erase a scientifically valid replication.

## Research policy and priority

Research-family preferences are versioned policy, not architecture.

Scheduler selection must emit a `PriorityDecision` containing policy version, eligible set, ordered criteria, reason codes, resource cost/starvation factors and selected task.

Undefined narrative labels such as `HIGH_VALUE_CANDIDATE` cannot drive scheduling.

## Negative Memory

Failure is durable but scoped. Negative records include failure scope, assumptions, regime context, source context, failure reason and revisit conditions/policy. They never imply `IDEA_FALSE_FOREVER` unless logically demonstrated.

Use bounded independent ideation before detailed archaeology/Negative-Memory comparison when anchoring risk matters.

## Evaluation membrane

Evaluation is a distinct future capability domain.

Research principal must not have outcome-store read capability when evaluation is activated.
Evaluator principal may ingest frozen export bundles and write sealed evaluation state but may not write Research state.
Research Supervisor must remain outcome-blind for active blinded epochs.
An influencing actor viewing sealed outcomes marks the epoch contamination state broken.

During an OPEN epoch, reverse messages are restricted to:

- `EXPORT_ACCEPTED`
- `EXPORT_REJECTED_FOR_SCHEMA_ERROR`
- `INTEGRITY_FAILURE`

Forbidden reverse messages include outcome, pass/fail, metrics, rank, portfolio contribution, outcome-derived blockers/retries and outcome-dependent completion signaling.

## Frozen export

Research creates `FROZEN_EXPORT_INTENT` binding candidate, trial-history, epoch, protocol, source/PIT, universe/clock/horizon/expression, cost/capacity/multiplicity and Validator hashes plus `research_head` and `export_bundle_hash`.

At export admission, the Validator artifact must bind the exact `candidate_hash`
as well as hypothesis/generation IDs, and its own canonical hash must be intact.
Historical Validator metadata without that binding remains historical evidence;
it cannot authorize a new export. Export universe, clock, horizon and economic
expression must preserve the Candidate's values. Any sealed-plane metadata in an
emitted export is included before calculating `export_bundle_hash`.

Evaluation may return only an `EVALUATION_INGEST_RECEIPT` proving receipt of that exact bundle and containing no outcome.

The technical receipt has exactly four fields: `event_type` (the literal
`EVALUATION_INGEST_RECEIPT`), `message` (one of the three allowed codes),
`export_bundle_hash` (lowercase hexadecimal SHA-256), and `receipt_hash` (the
canonical hash of the other three fields). No free-text extension fields or
structured export references are admitted. A receiver with a known frozen export
must compare `expected_export_bundle_hash`; a valid receipt for another bundle
cannot acknowledge its export. The deterministic pre-outcome pipeline exercises
that comparison. Payload/hash checks alone do not authenticate an evaluator,
establish runtime principal isolation or eliminate outcome-dependent timing.

After accepted export, material candidate/protocol/trial-history/epoch-policy mutation is forbidden. A material change requires a new generation/export.

## Feedback lineage

Economic feedback can become Research-visible only through a governed future `ECONOMIC_FEEDBACK_RELEASED` event and only for successor epochs.

It may not rewrite historical candidate, trial, discard, priority, Producer or Validator state.

Successor epochs declare `epoch_knowledge_parent` and `epoch_feedback_dependencies` so independent prospective epochs can be distinguished from adaptive post-feedback epochs.

## Concurrency and orchestration

Constitutional rule: one authoritative atomic transition per claim.

Initial bounded resource policy may use:

- `max_heavy_local_inference = 1`
- `max_authoritative_write_transition = 1`

GitHub is the qualified V2-initial authoritative orchestration backend under bounded-writer operation.

A future backend migration requires explicit proof and one authoritative source at a time; no dual orchestration truth.

P0-D server-side branch protection is not required.

## Required adversarial qualification

V2 tests must cover at least:

- hallucinated/malformed sources;
- broken source PIT and model-PIT classification;
- duplicate candidate and post-freeze mutation;
- undeclared model-policy change;
- ideation multiplicity accounting;
- Validator evidence contradiction, insufficiency and infrastructure error;
- close-policy mutation after first export;
- feedback release before allowed boundary;
- overlapping/adaptive epochs;
- research/supervisor outcome-access attempts;
- evaluator research-write attempt;
- forbidden reverse messages;
- stale claims, crash/retry and concurrent state change;
- bounded-writer GitHub outage/conflict behavior;
- unchanged four authority flags.

## Definition of Done

V2 Core may claim `AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED` only after evidence demonstrates all new V2 properties without opening economic/prospective/live authorities.

Future V2-E is a separate Owner-authorized phase and is not silently included in this implementation.
