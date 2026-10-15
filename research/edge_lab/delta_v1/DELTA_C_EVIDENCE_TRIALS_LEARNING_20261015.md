# DELTA C — Evidence, Trials & Learning

Date: 2026-10-15
Status: DECISIONAL RESEARCH ONLY
Branch: `research/delta-research-pack-v1-20261015`
Base: `93534d9c365b52f2aa80c4277da1cac4e7338d31`

## Decision question

What evidence model, trial-accounting rules and telemetry are required to know honestly what Quant-Trade knows, how many chances it gave itself to discover it, and whether the research process improves?

## Executive decision

The P0 evidence core must separate five concepts that were previously too easy to collapse:

```text
IDENTITY
GENERATION
LIFECYCLE
EVIDENCE
DECISION
```

A sixth concept — `OPERATIONAL_READINESS` — must remain outside scientific evidence.

The existing `E0–E7` idea may remain as a **human-readable summary**, but it must not be the source of truth and must never imply automatic linear promotion.

The source of truth should be a multidimensional evidence vector plus an independent decision state.

## 1. Canonical research identity

Minimum identity model:

```text
hypothesis_family_id
hypothesis_generation_id
parent_generation_ids[]
created_at
created_by
mechanism_id / mechanism_family
lifecycle_state
evidence_summary
research_decision
provenance
```

Human-readable example:

```text
HYP-0241-G3
LIFECYCLE = TESTED
EVIDENCE_SUMMARY = E2
DECISION = EXPLORE
```

These fields are orthogonal. A high evidence level does not force PROMOTE; a strong negative result can produce high evidence plus KILL.

## 2. Generation / amendment rule

### New generation required

A change is material if it can alter the set of admissible outcomes, the interpretation of the claim, or the decision map. Examples:

- signal definition;
- universe/population;
- holding horizon;
- primary endpoint;
- primary metric;
- outcome definition;
- eligibility rule;
- falsification scope;
- decision map;
- economic assumptions when they are claim-defining rather than preregistered stress cases;
- previously unauthorized secondary result elevated into the primary claim.

Any material post-freeze change creates a new generation with its own identity and prospective eligibility.

### Amendment only

A non-material amendment does not change any admissible result or decision. Examples:

- typo/documentation correction;
- display/UI change;
- variable rename with identical data and semantics;
- correction to a metadata field whose underlying bytes/data did not change;
- clarification that was already entailed by the frozen contract.

Every amendment is timestamped, justified and immutable.

### Ancestry is a DAG

The system must support branching:

```text
G1
├── G2A  horizon variant
├── G2B  alternative universe
└── G2C  alternative proxy/mechanism manifestation
```

No prior generation is overwritten.

`P0_REQUIRED = TRUE`

## 3. Evidence model

### Evidence vector

The machine-readable evidence model should be multidimensional:

```text
M — MECHANISM_EVIDENCE
M0 unknown
M1 plausible
M2 supported
M3 strongly supported

D — DATA_INTEGRITY
D0 unverified
D1 usable
D2 PIT/lineage validated
D3 independently audited or equivalently controlled

S — STATISTICAL_EVIDENCE
S0 none
S1 initial informative result
S2 internally robust under preregistered legitimate sensitivities
S3 independent holdout/OOS/replication
S4 prospective statistical survival

C — ECONOMIC_EVIDENCE
C0 unknown
C1 rough implementability screened
C2 realistic net economics assessed
C3 portfolio-economic viability assessed

P — PROSPECTIVE_EVIDENCE
P0 none
P1 valid prospective observation contract executed
P2 meaningful prospective sample accrued under frozen contract
P3 prospective survival established to the claim-appropriate standard
```

`O — OPERATIONAL_READINESS` is separate:

```text
O0 unavailable
O1 prototype capable
O2 shadow-ready
O3 deployment-ready
```

Operational readiness is not evidence that the edge exists.

### Evidence summary E0–E7

`RETAIN_AS_HUMAN_INTERFACE_ONLY`.

The summary may compress the vector for navigation/reporting, but:

- it must be derivable from the vector under a versioned rule;
- it must never grant authority;
- it must never erase dimensions;
- it must not imply every hypothesis follows one linear path.

## 4. Trial accounting

### Observed attempts are exact ledger facts

Record separately:

```text
observed_attempt_count
experiment_count
generation_count
replication_count
abandoned_attempt_count
failed_run_count
manual_exploration_count
```

A failed execution can be both operationally failed and statistically uninformative; it remains visible but is not automatically an effective statistical trial.

### Effective trials are an estimate/model, not a hidden exact field

```text
EFFECTIVE_TRIALS_STATUS =
KNOWN / ESTIMATED / PARTIALLY_BOUNDED / UNKNOWN

method
assumptions
covered_scope
limitations
estimate_value_or_interval
estimator_version
```

Rules:

- `UNKNOWN != 0`;
- `UNKNOWN != 1`;
- no count may be invented to satisfy downstream statistics;
- observed attempts and effective-trial estimates remain separate;
- new child IDs do not reset multiplicity history;
- researcher degrees of freedom must be logged where observable.

### Adaptive AI search

For autonomous/LLM research, record at minimum:

- number of candidate hypotheses proposed;
- evaluator/backtest calls;
- parameter/specification changes;
- datasets/universes queried;
- rejected candidates and reason;
- human interventions;
- model/tool version;
- validation surface exposures.

Repeated interaction with a fixed historical holdout can turn the holdout into training data; exposure history is therefore part of trial accounting.

## 5. Research decision model

Allowed decisions:

```text
KILL
PARK
EXPLORE
PROMOTE
NO_OPPORTUNITY
```

Decision and evidence are independent.

### KILL contract

Required:

```text
scope_of_falsification
reason
evidence_vector
claim_level_affected
authority
timestamp
```

A KILL never extends beyond the experiment's actual power to falsify.

### PARK contract

Use when the hypothesis remains scientifically/economically possible but current information, data, access or expected VOI does not justify spending now.

### EXPLORE contract

Use when additional information is rational despite high uncertainty. Rare mechanisms may remain EXPLORE when there is absence of proof rather than proof of absence.

### PROMOTE contract

PROMOTE means “eligible for the next evidence stage,” not “edge validated” and not “trade.” It requires explicit authority and cannot be derived automatically from a backtest/evidence score.

### NO_OPPORTUNITY

A native, auditable result. A future prediction ticket should allow calibrated abstention rather than forcing every research cycle to manufacture a candidate.

## 6. Decision-oriented Value of Information

Every material/expensive experiment should preregister a decision map:

```text
OUTCOME_A -> ACTION_A
OUTCOME_B -> ACTION_B
OUTCOME_C -> ACTION_C
DECISION_DIVERGENCE = HIGH / MEDIUM / LOW
```

Interpretation:

- HIGH: plausible outcomes would send research down materially different paths (e.g. PROMOTE vs KILL).
- MEDIUM: outcomes alter scope/resources but not direction completely.
- LOW: nearly every plausible outcome leads to the same next action.

This is preferable in P0 to an uncalibrated pseudo-precise numeric VOI.

## 7. Prospective proof

### Three independent axes

```text
EVIDENCE_TIMING =
RETROSPECTIVE / PROSPECTIVE / UNDETERMINED

PROSPECTIVE_INTEGRITY =
PASS / FAIL / NOT_ASSESSED / NOT_APPLICABLE

OBSERVATION_AUTHORIZATION =
NOT_AUTHORIZED / AUTHORIZED_FOR_EXACT_SCOPE
```

A valid prospective contract does not authorize actual prospective collection.

### Frozen prospective contract

At `PREDICTION_FROZEN_AT`, freeze at minimum:

- prediction;
- outcome definition;
- universe/population;
- observation/holding horizon;
- eligibility rules;
- primary metric;
- authorized secondary metrics;
- cost assumptions relevant to the claim;
- decision map;
- falsification scope;
- evidence target;
- exact data/source identities required to determine the outcome.

Store a canonical serialization and cryptographic content hash.

### Temporal integrity

Two distinct checks:

```text
INPUT_AVAILABILITY_CHECK
All information used to form the prediction must have been available no later than freeze time.

OUTCOME_AVAILABILITY_CHECK
Information sufficient to determine the declared outcome must not have been available at freeze time.
```

Prospective eligibility is evaluated against the **first availability** of the information required to determine the outcome, not when the researcher happened to notice it.

Any post-freeze material change creates a new prediction/generation with a new identity and its own prospective eligibility.

### Candidate timestamp fields

```text
PREDICTION_CREATED_AT
PREDICTION_FROZEN_AT
PROSPECTIVE_CONTRACT_HASH
OBSERVABLE_FROM
OUTCOME_FIRST_DETERMINABLE_AT
RESULT_RECORDED_AT
REALIZED_AT
```

Exact semantics must be documented by source type.

## 8. Learning telemetry

Do not build Meta-Research in P0. Retain telemetry from day one.

`P0_REQUIRED`:

```text
research_cost_proxy
wall_clock_time
time_to_falsification
duplication_flag / similarity_family
mechanism_family
observed_trials
effective_trials_status
kill_reason
park_reason
promote_reason
replication_status
calibration inputs/outcomes where probabilistic claim exists
OOS survival
prospective survival
novel mechanism flag
decision_changed_by_experiment
information_gain_class
```

Later portfolio telemetry such as marginal portfolio value is `DEFERRED` until portfolio evidence exists.

## 9. Proving that the research process learns

Do not use raw hit-rate improvement as proof.

### Cohort/prequential measures

Track future cohorts under frozen definitions:

```text
time_to_falsification
research_cost_per_resolved_decision
duplication_rate
calibration_error
effective_trials_per_validated_mechanism
prospective_survival
false_discovery_burden
information_gain_per_research_cost
```

### Frozen research benchmark tasks

`RETAIN_FOR_LATER_EVALUATION`.

Create a small hidden-answer benchmark set spanning:

- known real historical mechanism;
- known spurious anomaly;
- data-leakage trap;
- cost-destroyed anomaly;
- rare-but-real mechanism;
- duplicate/rephrased mechanism.

Future Research OS versions are compared on the same frozen tasks without revealing answers to the research loop. Benchmark reuse itself must be controlled so the benchmark does not become training data.

## Required DELTA C output

```text
IDENTITY_MODEL = P0_REQUIRED
GENERATION_AMENDMENT_RULE = P0_REQUIRED
ANCESTRY_DAG = P0_REQUIRED
EVIDENCE_VECTOR = P0_REQUIRED
E0_E7_SUMMARY = RETAIN_INTERFACE_ONLY
OPERATIONAL_READINESS_SEPARATE = P0_REQUIRED
DECISION_MODEL = P0_REQUIRED
TRIAL_ACCOUNTING_OBSERVED = P0_REQUIRED
EFFECTIVE_TRIAL_ESTIMATION = P0_REQUIRED_WITH_UNKNOWN_ALLOWED
PROSPECTIVE_PROOF_CONTRACT = P0_REQUIRED
REAL_PROSPECTIVE_OBSERVATION = NOT_AUTHORIZED
LEARNING_TELEMETRY = P0_REQUIRED
META_RESEARCH_ENGINE = DEFERRED
FROZEN_RESEARCH_BENCHMARKS = DEFERRED_TO_POST_P0_EVALUATION_DESIGN
```

## Governance compatibility

The verified Owner decisions already require strict multiplicity handling, separate discovery/validation streams, fixed endpoints, no rescue peeking, and separate authority for later phases. This DELTA operationalizes those principles rather than superseding them.

```text
OD01_OD12 = PASS
STRUCTURAL_PRE_OP = PASS
EXISTING_INVARIANTS = PASS
```

No evidence or recommendation here authorizes prospective collection, economic testing, Builder, live trading or capital.

## Key evidence used

- Harvey, Liu & Zhu, multiple-testing hurdle for financial factors.
- Chordia, Goyal & Saretto, false rejections in anomaly research.
- Hou, Xue & Zhang, large-scale anomaly replication.
- McLean & Pontiff, post-publication/OOS return decay.
- Federal Reserve SR 26-2, risk-based model inventory, effective challenge and aggregate dependency governance.
- 2026 agentic-finance evidence showing both constrained discovery potential and the danger of adaptive holdout contamination.
