# DELTA D — P0 Boundary

Date: 2026-10-15
Status: DECISIONAL RESEARCH ONLY
Branch: `research/delta-research-pack-v1-20261015`
Base: `93534d9c365b52f2aa80c4277da1cac4e7338d31`

## Decision question

What is the smallest system that can generate an auditable research decision without pretending to be a portfolio manager or trading system?

## Executive decision

P0 should be a **Minimum Scientific Kernel**, not a discovery engine and not a trading stack.

It should prove that Quant-Trade can preserve the scientific truth of a research cycle before adaptive discovery is allowed to increase the number of hypotheses.

`P0_DISCOVERY_ENGINE = NONE`

A fixed first cohort is enough to prove the kernel.

## FINAL_P0_CAPABILITIES

### RETAIN — P0 required

#### P0-1 Hypothesis identity + ancestry

Required:

```text
hypothesis_family_id
hypothesis_generation_id
parent_generation_ids[]
created_at
created_by
mechanism_family
branch_reason
```

Must support DAG branching and immutable prior generations.

#### P0-2 Preregistration + freeze + amendment log

Required:

- canonical frozen contract representation;
- freeze timestamp;
- content hash;
- material-change detector/rule;
- non-material amendment log;
- immutable historical versions.

#### P0-3 Minimal PIT / provenance

Required minimum:

```text
dataset_id
source
raw_or_snapshot_hash
retrieved_at
availability_rule
as_of / observation timestamp where applicable
transform_version
universe_definition
revision_status where applicable
```

P0 does **not** require a universal institutional data lineage platform. Add richer lineage only where the cohort actually requires it.

#### P0-4 Experiment + reproducible result

Required:

- experiment identity;
- frozen inputs/config;
- code/tool version;
- deterministic/reproducible result package where technically possible;
- result hash;
- execution status distinct from scientific result;
- no overwrite of prior result.

#### P0-5 Evidence assessment + decision state

Required:

- evidence vector `M/D/S/C/P`;
- operational readiness `O` separately;
- optional E-summary derived under a versioned mapping;
- decision `KILL/PARK/EXPLORE/PROMOTE/NO_OPPORTUNITY`;
- authority, timestamp, reason;
- `scope_of_falsification` for negative decisions.

No intelligent autonomous Decision Engine is required.

#### P0-6 Trial / effective-trial ledger

Required:

- observed attempts exact;
- failed/abandoned/manual attempts visible;
- ancestry-linked trial families;
- effective-trial status `KNOWN/ESTIMATED/PARTIALLY_BOUNDED/UNKNOWN`;
- method/assumptions/scope/limitations for estimates;
- no invented denominator.

#### P0-7 Prospective Observation Contract Ledger

Retain the **capability** to register and integrity-check prospective predictions.

Required:

- frozen prospective contract;
- timestamps and content hash;
- input-availability and outcome-availability checks;
- `EVIDENCE_TIMING`;
- `PROSPECTIVE_INTEGRITY`;
- `OBSERVATION_AUTHORIZATION` as an independent field.

Explicit boundary:

```text
REAL_PROSPECTIVE_OBSERVATION = NOT_AUTHORIZED
P0_MAY_TEST_CONTRACT_WITH_FIXTURES = TRUE
```

This is not a full Shadow Book.

#### P0-8 Economic Reality Stub

Retain as an early implementability screen, not as an execution optimizer.

Minimum candidate fields:

```text
instrument_available
data_available
spread_order_of_magnitude
fee_assumption
borrow_required
borrow_status
turnover_estimate
latency_requirement
capacity_obviously_blocked
```

Outputs:

```text
CURRENTLY_IMPLEMENTABLE = YES / NO / UNKNOWN
RESEARCH_WORTH_CONTINUING = YES / NO / UNKNOWN
BLOCK_REASON
OPTION_VALUE = NONE / LOW / MEDIUM / HIGH / UNKNOWN
```

The stub must never convert `CURRENTLY_IMPLEMENTABLE = NO` automatically into `KILL`.

#### P0-9 Learning telemetry

Retain data collection only:

```text
research_cost_proxy
wall_clock_time
time_to_falsification
duplication/similarity flag
mechanism family
observed/effective trials
reason for decision
replication status
calibration fields if probabilistic
OOS/prospective survival fields
decision_changed_by_experiment
information_gain_class
```

No Meta-Research optimizer in P0.

## DEFER

```text
FULL_PORTFOLIO_ENGINE = DEFER
FULL_SHADOW_BOOK = DEFER
FULL_EXECUTION_OPTIMIZER = DEFER
META_RESEARCH_ENGINE = DEFER
AUTOMATIC_RESEARCH_BUDGET_ALLOCATOR = DEFER
FUNDAMENTAL_AI_ENGINE = DEFER
CROSS_MARKET_ENGINE = DEFER
MICROSTRUCTURE_ENGINE = DEFER
REGIME_ENGINE = DEFER
MULTIPLE_DISCOVERY_ENGINES = DEFER_TO_POST_P0_OWNER_DECISION
LIVE_LAB_UX = DEFER_FROM_SCIENTIFIC_P0
ADVANCED_MULTI_AGENT_ORCHESTRATION = DEFER
```

## REJECT — P0

```text
CIO_AI = REJECT_P0
AUTONOMOUS_CAPITAL = REJECT_P0
LIVE_TRADING = REJECT_P0
AUTO_PROMOTION_TO_ECONOMIC_AUTHORITY = REJECT_P0
RETROSPECTIVE_TO_PROSPECTIVE_RECLASSIFICATION = REJECT_P0
MUTABLE_PAST_RESULTS = REJECT_P0
HIDDEN_FAILED_TRIALS = REJECT_P0
```

## UNKNOWN_WITH_REASON

### Exact implementation technology

`UNKNOWN_WITH_REASON`: architecture/technology belongs in the ADR/P0 Build Spec after Owner trajectory review, not in DELTA.

### Exact numeric evidence thresholds

`UNKNOWN_WITH_REASON`: OD parameters remain unresolved and cannot be silently inferred.

### Exact effective-trial estimator

`UNKNOWN_WITH_REASON`: depends on trial family/search process; P0 must support unknown/partial estimates rather than force one estimator.

## P0 acceptance tests

Acceptance tests prove contract implementation, not investment performance.

### AT-01 Immutable identity
Create HYP-G1, freeze it, mutate a material field. Expected: G1 unchanged; new generation required.

### AT-02 Non-material amendment
Correct documentation-only metadata. Expected: same generation, timestamped amendment log, scientific contract hash semantics preserved as defined.

### AT-03 Branching ancestry
Create two legitimate child variants from G1. Expected: DAG contains both children; neither overwrites the other.

### AT-04 Result immutability
Persist a result then attempt replacement. Expected: replacement rejected or versioned as a new result record under explicit correction semantics; original remains auditable.

### AT-05 Provenance
Given frozen dataset bytes/snapshot, verify stored hashes/source/availability metadata reproduce the declared input package.

### AT-06 Unknown trials
Set effective trials unknown. Expected: system stores `UNKNOWN`; no implicit zero/one; downstream output flags limitation.

### AT-07 Failed/abandoned attempt visibility
Record a failed run and abandoned specification. Expected: both remain in trial ledger with scientific-informativeness classification.

### AT-08 Decision/evidence orthogonality
Create high-confidence negative evidence. Expected: high evidence + KILL is legal. Create low-power rare result. Expected: low evidence + EXPLORE is legal.

### AT-09 Scope of falsification
Attempt family-wide KILL from a narrow single-universe experiment. Expected: rejected unless declared falsification scope actually covers the claim.

### AT-10 Promotion authority
Attempt PROMOTE without required authority. Expected: transition rejected and audit record persisted.

### AT-11 Prospective freeze
Freeze a prediction contract; alter outcome/horizon afterward. Expected: original remains immutable; new prediction/generation required.

### AT-12 Prospective integrity vs authorization
A fixture can have `PROSPECTIVE_INTEGRITY=PASS` while `OBSERVATION_AUTHORIZATION=NOT_AUTHORIZED`. Expected: system does not begin collection.

### AT-13 First-availability semantics
Fixture in which outcome information becomes public before researcher records it. Expected: prospective classification uses first availability, not observer awareness.

### AT-14 Early implementability is not Kill
`instrument_available = NO` with high research-transfer value. Expected: `CURRENTLY_IMPLEMENTABLE=NO` can coexist with `DECISION=EXPLORE/PARK`.

### AT-15 Decision map / VOI
Experiment with preregistered outcomes->actions. Expected: result maps to the frozen action rule; no post-result rewrite.

### AT-16 Control expectation is not mandatory result
Unexpected result on a diagnostic control. Expected: `INVESTIGATE`; system does not tune until expected outcome appears.

### AT-17 No unauthorized prospective collection
Invoke prospective collection path while authority false. Expected: hard block + audit record.

### AT-18 No Builder/economic authority inference
Scientific P0 capability passing tests must not alter Builder/capital/live-trading flags.

## FIRST_COHORT_CONTRACT

The first cohort is a research-system diagnostic cohort, separate from acceptance tests.

Starting composition:

```text
CASE_1 = POSITIVE_CONTROL
Known historical phenomenon with a preregistered diagnostic expectation.

CASE_2 = NEGATIVE_CONTROL
Placebo/relation expected to fail.

CASE_3 = FRAGILE_ANOMALY
Known/suspected effect expected to weaken under PIT/cost/multiplicity discipline.

CASE_4 = REAL_NOVEL_QUANT_TRADE_CANDIDATE
A genuine research hypothesis not selected because it is likely to succeed.
```

Rules:

- diagnostic expectations are not mandatory statistical outcomes;
- unexpected controls trigger investigation of data/implementation/protocol sensitivity;
- no tuning until expected result appears;
- cohort cases are preregistered before outcomes are accessed under the applicable authority;
- real prospective observation, economic testing and any historical acquisition requiring new authority remain separately gated;
- cohort success does not require PROMOTE.

A cohort outcome such as:

```text
1 KILL
2 EXPLORE
1 PARK
0 PROMOTE
```

can be complete P0 success.

## P0 success definition

P0 succeeds if it can demonstrably:

```text
REGISTER
FREEZE
VERSION MATERIAL CHANGES
AMEND NON-MATERIAL CHANGES
PRESERVE ANCESTRY
EXECUTE / IMPORT AN AUTHORIZED EXPERIMENT
REPRODUCE RESULT
COUNT OBSERVED TRIALS
REPRESENT EFFECTIVE-TRIAL UNCERTAINTY
PRESERVE PROVENANCE
ASSESS MULTIDIMENSIONAL EVIDENCE
REJECT
PARK
EXPLORE
PROMOTE ONLY WITH AUTHORITY
REPRESENT NO_OPPORTUNITY
REGISTER PROSPECTIVE CONTRACTS WITHOUT AUTO-COLLECTION
AUDIT EVERYTHING AFTERWARD
```

It does **not** succeed because it finds an edge.

## P0_OUT_OF_SCOPE

No portfolio allocation, live execution, autonomous CIO, live capital, full Shadow Book, discovery federation, Meta-Research engine, or Live Lab visualization is necessary to satisfy P0 scientific acceptance.

## BLOCKERS_BEFORE_ADR

```text
1. OWNER review of DELTA final matrix / trajectory recommendation.
2. Resolve any explicit governance conflict if one is identified.
3. Preserve unresolved OD numerical/statistical parameters as unresolved.
```

No other architecture-brainstorming loop is required by default.

## Governance compatibility

```text
OD01_OD12 = PASS
STRUCTURAL_PRE_OP = PASS
EXISTING_INVARIANTS = PASS
```

This DELTA recommendation does not authorize Builder, prospective observation, economic experiments, live trading or real capital.
