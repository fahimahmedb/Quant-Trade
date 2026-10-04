# OWNER — WEATHER V4 A2 DEDICATED HARNESS BUILDER DECISION — 2026-10-04

OWNER_AUTHORITY_BASE_SHA =
9b65151c6840cff9d6cad4b6ba897e329862d292

MISSION_CLASS =
OWNER_BUILDER_AUTHORIZATION_FOR_DEDICATED_A2_HARNESS_CONSTRUCTION_ONLY

A2_HARNESS_DIRECTION =
DEDICATED_A2_HARNESS

AUTHORITY_BASIS =
Blue read-only suitability assessment at commit 9b65151c6840cff9d6cad4b6ba897e329862d292.

## 1. Exact Builder authorization

BUILDER_AUTHORIZED =
TRUE_FOR_DEDICATED_A2_HARNESS_CONSTRUCTION_ONLY

AUTHORIZED_SCOPE =
Implement a new dedicated Weather V4 A2 offline harness whose structure supports the already-defined A2 documentary contract.

The Builder may implement only:

- explicit input-manifest binding;
- explicit output-manifest binding;
- fixture provenance/lineage checks;
- reader/release role declarations;
- logging interfaces;
- quarantine state handling;
- fail-closed STOP semantics;
- output restriction;
- cumulative-disclosure state;
- deterministic offline interface;
- exact authority/version binding.

The historical Gate-B runner must remain unchanged.

HISTORICAL_GATE_B_RUNNER_MUTATION_AUTHORIZED =
FALSE

HISTORICAL_GATE_B_RUNNER_PATH =
governance/run_gate_b_evidence_schema_discriminants_2026-09-21.py

## 2. Explicit non-authorizations

BUILDER_IMPLEMENTATION_TEST_EXECUTION =
NOT_AUTHORIZED_YET

A2_FIXTURE_GENERATION_AUTHORIZED =
FALSE

A2_FIXTURE_TESTING_AUTHORIZED =
FALSE

A2_EXECUTION_AUTHORIZED =
FALSE

The following are NOT authorized:

- running the new harness;
- running tests;
- generating actual fixtures;
- testing actual fixtures;
- opening existing outcome-bearing fixtures;
- accessing real data;
- accessing real metadata;
- querying endpoints;
- using credentials;
- selecting sources, stations, models or cities;
- economic analysis;
- backtesting;
- PnL measurement;
- capture;
- DATA_T0;
- EXPERIMENT_T0;
- paper trading;
- live trading;
- real capital.

## 3. Construction boundary

Construction must remain offline and implementation-only.

The Builder may create code, schemas, interfaces and documentary artifacts needed to implement the dedicated A2 harness, provided they do not require prohibited data, metadata, fixtures, endpoints, credentials or economic assumptions.

The Builder must not claim that implemented controls are effective merely because code exists.

IMPLEMENTATION_COMPLETE != CONTROL_EFFECTIVENESS_VERIFIED

IMPLEMENTATION_COMPLETE != A2_EXECUTION_AUTHORIZED

IMPLEMENTATION_COMPLETE != A2_HARNESS_APPROVED

## 4. STOP condition

BUILDER_STOP_REQUIRED =
TRUE_IF_ADDITIONAL_AUTHORITY_REQUIRED

The Builder must STOP if construction requires any of the following:

- access to existing fixtures;
- fixture generation;
- fixture execution/testing;
- real data;
- real metadata;
- endpoint access;
- credentials;
- operational source selection;
- economic assumptions;
- validation outcomes;
- any authority beyond implementation-only construction.

If stopped, return the exact missing authority and do not infer, simulate, work around or expand scope.

## 5. Required design properties

The dedicated harness must be designed so that future authorized execution can bind explicitly to:

- exact owner authority SHA;
- exact input manifest;
- exact output manifest;
- explicit allowed input classes;
- explicit prohibited input classes;
- fixture provenance/lineage metadata;
- exact reader roles;
- exact release roles;
- immutable or append-only logging interface semantics;
- quarantine state;
- fail-closed STOP state;
- output-release restriction;
- cumulative-disclosure state;
- deterministic offline execution contract;
- exact harness version/commit binding.

No future execution permission is implied by implementing these interfaces.

## 6. Governance state

ECONOMIC_AUTHORITY =
0

CAPTURE_AUTHORIZATION =
NONE

DATA_T0 =
NOT_DECLARED

EXPERIMENT_T0 =
NOT_DECLARED

REAL_CAPITAL_AUTHORIZED =
FALSE

LIVE_TRADING_AUTHORIZED =
FALSE

REAL_DATA_ACCESS =
NONE

REAL_METADATA_ACCESS =
NONE

ENDPOINT_ACCESS =
NONE

CREDENTIAL_USE =
NONE

OBSERVATION_AUTHORITY =
UNCHANGED

## 7. Required Builder handoff

The Builder must return a bounded implementation handoff containing at minimum:

BRANCH
COMMIT_SHA
PARENT_SHA
OWNER_AUTHORITY_VERIFIED
FILES_CREATED
FILES_MODIFIED
FILES_MODIFIED_OUTSIDE_SCOPE
DEDICATED_A2_HARNESS_PATH
HISTORICAL_GATE_B_RUNNER_MODIFIED
INPUT_MANIFEST_BINDING_IMPLEMENTED
OUTPUT_MANIFEST_BINDING_IMPLEMENTED
PROVENANCE_LINEAGE_INTERFACE_IMPLEMENTED
ROLE_DECLARATION_INTERFACE_IMPLEMENTED
LOGGING_INTERFACE_IMPLEMENTED
QUARANTINE_STATE_IMPLEMENTED
FAIL_CLOSED_STOP_IMPLEMENTED
OUTPUT_RESTRICTION_IMPLEMENTED
CUMULATIVE_DISCLOSURE_STATE_IMPLEMENTED
DETERMINISTIC_OFFLINE_INTERFACE_IMPLEMENTED
AUTHORITY_VERSION_BINDING_IMPLEMENTED
FIXTURES_ACCESSED
FIXTURES_CREATED
CODE_EXECUTED
TESTS_RUN
REAL_DATA_ACCESSED
REAL_METADATA_ACCESSED
ENDPOINTS_QUERIED
CREDENTIALS_USED
A2_EXECUTION_AUTHORIZED
BUILDER_AUTHORIZED_SCOPE
ECONOMIC_AUTHORITY
TERMINAL_STATE
NEXT_SAFE_ACTION

Expected invariants:

HISTORICAL_GATE_B_RUNNER_MODIFIED = FALSE
FIXTURES_ACCESSED = NONE
FIXTURES_CREATED = NONE
CODE_EXECUTED = NO
TESTS_RUN = NO
REAL_DATA_ACCESSED = NONE
REAL_METADATA_ACCESSED = NONE
ENDPOINTS_QUERIED = NONE
CREDENTIALS_USED = NONE
A2_EXECUTION_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0

## 8. Next safe action

NEXT_SAFE_ACTION =
BUILDER_DEDICATED_A2_HARNESS_CONSTRUCTION_ONLY
