# OWNER — WEATHER V4 A2 BOUNDED OFFLINE HARNESS TEST AUTHORITY — 2026-10-05

MANDATORY_ASTRA_PASS_SHA =
976da7e0190b899bd9982e9e0565d68fecdddb6d

MANDATORY_AUDITED_HARNESS_SHA =
2bc718711d507b38176981c2b3e55dd607c9547b

MISSION_CLASS =
OWNER_AUTHORIZATION_FOR_BOUNDED_OFFLINE_A2_HARNESS_RUNTIME_TESTING_ONLY

STATIC_A2_HARNESS_STATUS =
PASSED_INDEPENDENT_STATIC_AUDIT

OWNER_AUTHORIZES =
BOUNDED_OFFLINE_HARNESS_RUNTIME_TESTING_ONLY

A2_EXECUTION_AUTHORIZED =
FALSE

A2_FIXTURE_GENERATION_AUTHORIZED =
FALSE

A2_FIXTURE_TESTING_AUTHORIZED =
FALSE

RESEARCH_FIXTURE_GENERATION_AUTHORIZED =
FALSE

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

## 1. Purpose

This Owner decision authorizes a bounded offline runtime-test phase for the dedicated Weather V4 A2 harness after the exact independent Astra static PASS at commit 976da7e0190b899bd9982e9e0565d68fecdddb6d.

The purpose is only to verify that the already-audited governance invariants behave as intended when the harness is executed offline.

This is NOT authorization to execute the A2 research phase or any economic experiment.

RUNTIME_TEST_PASS
!=
A2_EXECUTION_AUTHORIZATION

RUNTIME_TEST_PASS
!=
RESEARCH_FIXTURE_APPROVAL

RUNTIME_TEST_PASS
!=
ECONOMIC_VALIDATION

## 2. Authorized execution

The test agent / Builder is authorized to:

- execute the dedicated A2 harness offline;
- import the dedicated A2 harness for testing;
- create deterministic unit and adversarial tests limited to governance semantics;
- create test-only synthetic structural objects required to exercise those semantics;
- run those bounded tests locally/offline;
- inspect test output produced by those tests;
- repair test code itself if needed;
- repair production harness code only if a runtime test exposes a genuine defect in an invariant already authorized and audited statically, provided the repair remains strictly inside `research/weather_forward/v4/a2_harness/` and does not widen capability or authority;
- rerun the bounded offline tests after such an in-scope repair;
- persist documentary test evidence and test files within the dedicated Weather V4 A2 area.

AUTONOMY_INSIDE_AUTHORIZED_TEST_SCOPE =
MAXIMIZED

DESIGN_AMBIGUITY =
TEST_AGENT_DECIDES_CONSERVATIVELY_AND_CONTINUES

AUTHORITY_AMBIGUITY =
STOP

## 3. Exact test target

The test phase must begin from exact static-audited harness lineage:

ASTRA_PASS_SHA =
976da7e0190b899bd9982e9e0565d68fecdddb6d

AUDITED_HARNESS_SHA =
2bc718711d507b38176981c2b3e55dd607c9547b

The test branch must descend from this Owner authority artifact and therefore preserve the audited harness lineage.

## 4. Required runtime invariants

The bounded test suite must exercise, at minimum, the following classes of behavior.

### D1 — trusted execution-policy root

Verify runtime fail-closed behavior when the production trusted root is absent.

The default production state must remain:

CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT = NONE

NO_TRUSTED_EXECUTION_POLICY_ROOT = DENY_ALL_PERMIT_RELEASE_ADMISSION_PATHS

A test may use a synthetic test-only trusted-root object or test-only monkeypatch/injection solely to exercise positive and mismatch branches. Such a test root:

- exists only inside test process state;
- is not written into `trusted_root.py` as a production root;
- is not execution authority;
- is not Owner authorization;
- must use obviously synthetic identifiers;
- must never be reused outside the bounded test suite.

TEST_ONLY_TRUSTED_ROOT != EXECUTION_POLICY_AUTHORITY

### D2 — fixture provenance contract

Use only test-only structural metadata objects, never research fixtures or outcome-bearing fixtures.

Test rejection/acceptance semantics for exact fixture identity, generator identity/version, construction classes, lineage, reproducibility keys, contamination/admissibility and digest binding.

A test-only `FixtureProvenance` object is metadata-only and does NOT constitute `A2_FIXTURE_GENERATION_AUTHORIZED`.

### D3 — exact recipient authorization

Test exact actor-id + role authorization separately from cumulative disclosure.

### D4 — independent release approval

Test that REQUIRED release approval rejects identical release-actor / recipient identity and preserves role/action/authority/state checks.

### D5 — final-state logging invariant

Test that public direct construction cannot manufacture permissive/authorized completed state without exact acknowledged log linkage.

Test the guarded path for:

- successful append acknowledgement;
- exact record ID;
- exactly one matching record;
- exact record equality;
- authority/actor/action/target/context equality;
- `AUTHORIZED => PERMIT`;
- permissive => `COMPLETED + VALID`;
- same record ID with materially different content => reject;
- duplicate or missing log ID => fail closed.

### Other preserved invariants

Test at minimum:

- exact input manifest binding;
- exact output manifest binding;
- wrong manifest digest => fail closed;
- actor mismatch => fail closed;
- role mismatch => fail closed;
- action mismatch => fail closed;
- execution-policy authority mismatch => fail closed;
- authorization-state mismatch => fail closed;
- exact cumulative-disclosure tuple `output_id + recipient_actor_id + recipient_role`;
- empty disclosure ledger => `UNRESOLVED`;
- global `BLOCKED` precedence;
- resource boundary `UNRESOLVED` / `EXCEEDED` => fail closed;
- `ResourceBoundaryState.WITHIN_AUTHORITY` exact value remains `WITHIN_AUTHORITY`.

## 5. Test framework / implementation autonomy

The test agent may autonomously choose the smallest auditable standard-library test design.

Preferred default:

- Python standard library `unittest`;
- `unittest.mock` where necessary for test-only dependency substitution;
- no new external dependency unless strictly unavoidable.

If the repository already has a compatible existing test framework and using it does not widen scope, the test agent may use it.

EXTERNAL_DEPENDENCY_ADDITION =
NOT_AUTHORIZED_BY_DEFAULT

The test agent should not stop for ordinary questions about file names, helper functions, test class structure, synthetic IDs or test-case decomposition.

## 6. Allowed mutation scope

The test agent may modify or create files only under:

research/weather_forward/v4/a2_harness/

This includes test modules and local documentary test evidence.

Production harness code may be modified only when a runtime test exposes a genuine defect in an already-authorized invariant and the repair is necessary to make the audited contract true at runtime.

If such production repair occurs, the handoff must identify it exactly and the final state requires independent Astra review before any further authority.

Do NOT modify:

- `src/`;
- historical Gate-B runner;
- historical fixtures;
- Owner artifacts;
- Blue artifacts;
- Astra artifacts;
- unrelated repository files.

## 7. Explicitly prohibited activity

This authority does NOT authorize:

- execution of the A2 experiment;
- generation of research/A2 fixtures;
- outcome-bearing fixtures;
- access to existing outcome-bearing fixtures;
- real data;
- real metadata;
- external endpoints;
- credentials;
- network calls;
- source selection;
- station selection;
- city selection;
- forecast-model selection;
- market selection;
- cadence measurement;
- capture;
- `DATA_T0` declaration;
- `EXPERIMENT_T0` declaration;
- backtests;
- PnL;
- economic scoring;
- paper trading;
- live trading;
- capital allocation.

No test may read real repository fixture payloads merely because they are locally available.

## 8. Test-only synthetic object rule

TEST_ONLY_SYNTHETIC_STRUCTURAL_OBJECTS_ALLOWED = TRUE

Such objects must be:

- deterministic;
- obviously synthetic;
- created only for testing governance code paths;
- non-economic;
- non-outcome-bearing;
- not calibrated from real-world efficacy information;
- not derived from real data or real metadata;
- not persisted as research evidence.

They may represent manifests, actors, authorizations, disclosure records, provenance metadata, log records, trusted-root test doubles and resource-boundary states strictly for test purposes.

## 9. Evidence and completion semantics

The test agent must report:

- exact branch / commit / parent;
- exact Owner authority SHA;
- exact Astra PASS SHA;
- files created/modified;
- production harness files modified, if any;
- exact command(s) run;
- test framework;
- number of tests collected/run/passed/failed/skipped/error;
- each required invariant coverage status;
- whether any runtime defect was found;
- whether any production code repair was required;
- whether rerun after repair passed;
- whether any external dependency was added;
- whether any real data/metadata/fixture/endpoint/credential/network access occurred.

A green test suite establishes only bounded runtime evidence for the harness under the exercised synthetic cases.

It does NOT establish exhaustive runtime correctness or deployed control effectiveness.

BOUNDED_OFFLINE_TEST_PASS
!=
RUNTIME_CONTROL_EFFECTIVENESS_FULLY_VERIFIED

## 10. Terminal states

Allowed terminal states:

BOUNDED_OFFLINE_HARNESS_TEST_PASS

BOUNDED_OFFLINE_HARNESS_TEST_FAIL

BLOCKED_BY_UNRESOLVED_AUTHORITY

If tests expose a defect and it is safely repairable inside this exact authority, repair it autonomously, rerun, and report the full repair lineage.

If repair would require authority outside this artifact, STOP.

## 11. Required next action

If final bounded tests PASS:

NEXT_SAFE_ACTION =
ASTRA_INDEPENDENT_RUNTIME_TEST_EVIDENCE_AUDIT_ONLY

If final bounded tests FAIL or remain unresolved:

NEXT_SAFE_ACTION =
OWNER_REVIEW_OF_RUNTIME_TEST_DEFECTS_ONLY

## 12. Hard governance invariants

A2_FIXTURE_GENERATION_AUTHORIZED = FALSE
A2_FIXTURE_TESTING_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0
CAPTURE_AUTHORIZATION = NONE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED
