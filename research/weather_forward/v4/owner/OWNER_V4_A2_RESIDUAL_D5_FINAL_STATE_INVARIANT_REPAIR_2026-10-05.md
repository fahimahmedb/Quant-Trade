# OWNER — WEATHER V4 A2 RESIDUAL D5 FINAL-STATE INVARIANT REPAIR — 2026-10-05

MANDATORY_ASTRA_RECHECK_SHA =
2602b993a98ef565a164e48bf4c801b0b86a8994

AUDITED_BUILDER_TARGET =
fa81d3fbddca2802e43ea0b05fe85e608b98a61d

MISSION_CLASS =
OWNER_AUTHORIZATION_FOR_RESIDUAL_D5_FINAL_STATE_INVARIANT_REPAIR_ONLY

D1_STATUS = CLOSED
D2_STATUS = CLOSED
D3_STATUS = CLOSED
D4_STATUS = CLOSED
D5_STATUS = STILL_OPEN_DIRECT_CONSTRUCTOR_BYPASS_ONLY

BUILDER_AUTHORIZED =
TRUE_FOR_RESIDUAL_D5_FINAL_STATE_INVARIANT_REPAIR_ONLY

AUTONOMY_INSIDE_AUTHORIZED_REPAIR_SCOPE =
MAXIMIZED

AUTHORITY_EXPANSION =
PROHIBITED

## 1. Exact residual defect

Astra recheck established that the remaining defect is confined to the public final-state type boundary.

`HarnessDecision` and `LoggedActionResult` are publicly constructible final-state models. Their current construction semantics allow a caller to directly manufacture semantically final permissive states such as:

- `PermitState.PERMIT`;
- `ReleaseState.AUTHORIZED`;
- `CompletionState.COMPLETED`;

without proving that the required exact log append was successfully acknowledged.

This leaves the following invariant unenforced at the public final-state boundary:

FINAL_PERMIT_OR_AUTHORIZED
=>
REQUIRED_LOG_ACKNOWLEDGED
AND
EXACT_LOG_RECORD_PRESENT_IN_RETURNED_LOG

The three public evaluate-and-log APIs are not themselves the residual defect; Astra confirmed they append and acknowledge before returning their own completed permissive result.

## 2. Authorized repair

The Builder is authorized to close only this residual D5 construction bypass.

Builder may autonomously choose the smallest auditable static design, including one or more of:

- guarded/private constructors;
- internal/private raw decision types;
- factory-only creation of final permissive result objects;
- `__post_init__` invariants;
- acknowledgement-bound construction objects/tokens;
- structural validation that a permissive/completed `LoggedActionResult` references an exact acknowledged `LogRecord` that is present in the returned `StructuredAuditLog`;
- removal of unsafe public re-exports where helpful.

The repaired source must enforce, at the final public result boundary, that a permissive or authorized completed result cannot be validly constructed without exact acknowledged logging linkage.

The repair does NOT need deployed tamper-proof logging, cryptographic storage, external persistence or runtime proof.

## 3. Required final-state invariant

For any public final result representing a completed authority-bearing action:

IF

- `permit_or_deny_state = PERMIT`; or
- `release_state = AUTHORIZED`; or
- another equivalent completed permissive semantic is represented;

THEN all of the following must be structurally required:

- `log_acknowledged = TRUE`;
- `log_record` is present;
- the exact `log_record.record_id` exists in the returned `StructuredAuditLog`;
- the record in the returned log exactly matches the linked result record for the material logged fields;
- the final result cannot be constructed through a public bypass that omits this linkage.

If the required exact log linkage is absent or inconsistent, construction/finalization must fail closed or the object must remain non-permissive / not completed.

## 4. Preserve closed findings

The Builder must preserve without regression:

- D1 trusted execution-policy root closure;
- current trusted execution-policy root = NONE;
- deny-all while no trusted execution-policy root exists;
- D2 exact fixture provenance/lineage closure;
- D3 exact recipient authorization closure;
- D4 release actor / recipient identity separation;
- exact input manifest binding;
- exact output manifest binding;
- exact cumulative-disclosure tuple semantics;
- BLOCKED precedence;
- role/action/authority/state fail-closed behavior;
- static determinism;
- no permissive fallback.

## 5. Repository scope

Builder may modify only:

research/weather_forward/v4/a2_harness/

Builder may modify only the files necessary to close residual D5 and update local documentation/exports consistently.

Do NOT modify:

- `src/`;
- historical Gate-B runner;
- fixtures;
- Owner artifacts;
- Blue artifacts;
- Astra artifacts;
- unrelated repository files.

## 6. Absolute non-authorizations

CODE_EXECUTION_AUTHORIZED = FALSE
TEST_EXECUTION_AUTHORIZED = FALSE
A2_FIXTURE_GENERATION_AUTHORIZED = FALSE
A2_FIXTURE_TESTING_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
REAL_DATA_ACCESS = NONE
REAL_METADATA_ACCESS = NONE
ENDPOINT_ACCESS = NONE
CREDENTIAL_USE = NONE
CAPTURE_AUTHORIZATION = NONE
ECONOMIC_AUTHORITY = 0
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED

Builder must NOT run Python, imports, tests, pytest, linters, type checkers or CI.
Builder must NOT inspect or generate fixtures, access real data/metadata, query endpoints, use credentials, perform backtests/PnL/economic analysis, or activate A2.

## 7. Autonomy and STOP rule

DESIGN_AMBIGUITY = BUILDER_DECIDES_CONSERVATIVELY_AND_CONTINUES
AUTHORITY_AMBIGUITY = BUILDER_STOPS

Do not return for ordinary implementation choices.
If an in-scope directly related defect is found during static self-review, fix it autonomously.

STOP only if closing this residual D5 defect genuinely requires authority outside this artifact.

## 8. Completion meaning

Successful repair meaning:

RESIDUAL_D5_FINAL_STATE_INVARIANT_STATIC_REPAIR_COMPLETE

This does NOT mean runtime verified, control effectiveness verified, A2 approved, A2 execution authorized, fixture approved or economically validated.

## 9. Required Builder handoff

Return at minimum:

BRANCH
COMMIT_SHA
PARENT_SHA
OWNER_RESIDUAL_D5_AUTHORITY_VERIFIED
ASTRA_RECHECK_SHA_VERIFIED
FILES_MODIFIED
FILES_CREATED
FILES_MODIFIED_OUTSIDE_SCOPE

FINAL_PERMISSIVE_RESULT_GUARDED
DIRECT_HARNESS_DECISION_BYPASS_CLOSED
DIRECT_LOGGED_ACTION_RESULT_BYPASS_CLOSED
EXACT_ACKNOWLEDGED_LOG_LINK_REQUIRED
EXACT_LOG_RECORD_PRESENT_IN_RETURNED_LOG_REQUIRED
PUBLIC_UNSAFE_REEXPORTS_CLOSED_OR_GUARDED

D1_REGRESSION_FOUND
D2_REGRESSION_FOUND
D3_REGRESSION_FOUND
D4_REGRESSION_FOUND
OTHER_STATIC_REGRESSION_FOUND
KNOWN_IN_SCOPE_DEFECTS_LEFT_UNFIXED
STATIC_SELF_REVIEW_COMPLETE

HISTORICAL_GATE_B_RUNNER_MODIFIED
SRC_MODIFIED
FIXTURES_ACCESSED
FIXTURES_CREATED
CODE_EXECUTED
TESTS_RUN
REAL_DATA_ACCESSED
REAL_METADATA_ACCESSED
ENDPOINTS_QUERIED
CREDENTIALS_USED

A2_EXECUTION_AUTHORIZED
ECONOMIC_AUTHORITY
CAPTURE_AUTHORIZATION
DATA_T0
EXPERIMENT_T0

TERMINAL_STATE
ADDITIONAL_AUTHORITY_REQUIRED
NEXT_SAFE_ACTION

Expected successful values:

FILES_MODIFIED_OUTSIDE_SCOPE = NONE
FINAL_PERMISSIVE_RESULT_GUARDED = TRUE
DIRECT_HARNESS_DECISION_BYPASS_CLOSED = TRUE
DIRECT_LOGGED_ACTION_RESULT_BYPASS_CLOSED = TRUE
EXACT_ACKNOWLEDGED_LOG_LINK_REQUIRED = TRUE
EXACT_LOG_RECORD_PRESENT_IN_RETURNED_LOG_REQUIRED = TRUE
PUBLIC_UNSAFE_REEXPORTS_CLOSED_OR_GUARDED = TRUE
D1_REGRESSION_FOUND = FALSE
D2_REGRESSION_FOUND = FALSE
D3_REGRESSION_FOUND = FALSE
D4_REGRESSION_FOUND = FALSE
OTHER_STATIC_REGRESSION_FOUND = FALSE
KNOWN_IN_SCOPE_DEFECTS_LEFT_UNFIXED = NONE
STATIC_SELF_REVIEW_COMPLETE = TRUE
HISTORICAL_GATE_B_RUNNER_MODIFIED = FALSE
SRC_MODIFIED = FALSE
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
CAPTURE_AUTHORIZATION = NONE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED

TERMINAL_STATE = RESIDUAL_D5_FINAL_STATE_INVARIANT_STATIC_REPAIR_COMPLETE
NEXT_SAFE_ACTION = ASTRA_RESIDUAL_D5_STATIC_RECHECK_ONLY
