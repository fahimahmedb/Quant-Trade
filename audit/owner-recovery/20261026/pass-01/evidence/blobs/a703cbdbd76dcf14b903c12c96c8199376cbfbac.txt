# ASTRA — WEATHER V4 A2 RESIDUAL D5 FINAL STATIC RECHECK — 2026-10-05

AUDIT_BRANCH = astra/weather-v4-a2-residual-d5-final-static-recheck-2026-10-05
AUDIT_PARENT_SHA = 2bc718711d507b38176981c2b3e55dd607c9547b
AUDIT_TARGET_SHA = 2bc718711d507b38176981c2b3e55dd607c9547b

MISSION_CLASS = FINAL_INDEPENDENT_ADVERSARIAL_STATIC_RECHECK_WEATHER_V4_A2_RESIDUAL_D5_FINAL_STATE_INVARIANT

MANDATORY_OWNER_AUTHORITY = d1447fd515e814a21e34118d0a0b063a44220bbd
MANDATORY_PRIOR_ASTRA_RECHECK = 2602b993a98ef565a164e48bf4c801b0b86a8994
PRIOR_BUILDER_TARGET = fa81d3fbddca2802e43ea0b05fe85e608b98a61d

OWNER_AUTHORITY_VERIFIED = TRUE
PRIOR_ASTRA_RECHECK_VERIFIED = TRUE
BUILDER_LINEAGE_VERIFIED = TRUE

Required lineage resolved:

fa81d3fbddca2802e43ea0b05fe85e608b98a61d
-> 2602b993a98ef565a164e48bf4c801b0b86a8994
-> d1447fd515e814a21e34118d0a0b063a44220bbd
-> 2bc718711d507b38176981c2b3e55dd607c9547b

Builder branch exact HEAD verified at 2bc718711d507b38176981c2b3e55dd607c9547b.

## Files reviewed

- research/weather_forward/v4/a2_harness/contract.py @ 2bc718711d507b38176981c2b3e55dd607c9547b
- research/weather_forward/v4/a2_harness/harness.py @ 2bc718711d507b38176981c2b3e55dd607c9547b
- research/weather_forward/v4/a2_harness/__init__.py @ 2bc718711d507b38176981c2b3e55dd607c9547b as needed for public exposure
- research/weather_forward/v4/owner/OWNER_V4_A2_RESIDUAL_D5_FINAL_STATE_INVARIANT_REPAIR_2026-10-05.md @ d1447fd515e814a21e34118d0a0b063a44220bbd
- research/weather_forward/v4/audit/ASTRA_V4_A2_D1_D5_STATIC_RECHECK_2026-10-05.md @ 2602b993a98ef565a164e48bf4c801b0b86a8994

## Residual D5 finding

D5_STATUS = CLOSED

The prior direct-constructor bypass is closed at the supported public final-state boundary.

`HarnessDecision` remains publicly exported but is now `init=False` with an explicit public constructor that rejects any state where `permit_or_deny_state == PERMIT` or `release_state == AUTHORIZED`. Direct public construction therefore cannot create a permissive or authorized final decision.

`LoggedActionResult` remains publicly exported but its public constructor rejects any permissive decision and also rejects any direct attempt to claim acknowledged linkage by setting `log_acknowledged = TRUE` or supplying a non-null `log_record`. Direct construction therefore cannot manufacture a valid acknowledged permissive result.

The only source path that constructs permissive final state is the private guarded finalization path. `_new_guarded_harness_decision` and `_finalize_logged_action_result` are private underscore-prefixed helpers and are not re-exported through package `__all__`. Under the mandated Python encapsulation standard, deliberate manual invocation of private/internal object-model mechanisms is not treated as a supported public API bypass.

DIRECT_HARNESS_DECISION_BYPASS = CLOSED
DIRECT_LOGGED_ACTION_RESULT_BYPASS = CLOSED

## Guarded finalizer audit

`_finalize_logged_action_result()` statically requires all of the following before returning a final linked result:

- `acknowledgement.appended == TRUE`;
- `acknowledgement.record_id == log_record.record_id`;
- exactly one record with that ID in `acknowledgement.log`;
- that exact stored record equals the linked `log_record` dataclass value;
- construction authority matches expected construction authority;
- execution-policy authority matches expected execution-policy authority;
- authorization authority matches expected authorization authority;
- actor ID and actor role match;
- authorization ID matches;
- attempted action matches;
- target kind and target ID match;
- manifest/provenance identity matches;
- incident context matches;
- cumulative-disclosure context matches;
- recipient actor and role match where applicable;
- permit state, release state and quarantine state match the linked record;
- `AUTHORIZED` release requires `PERMIT`;
- `DENY` cannot pair with a non-blocked release;
- any permissive state requires `completion_state == COMPLETED`;
- any permissive state requires `validation_state == VALID`.

Same-record-ID but materially different-record substitution is rejected because the unique record from the acknowledged log must equal the supplied linked `LogRecord` across all dataclass fields.

EXACT_ACKNOWLEDGED_LOG_LINK = PASS
EXACT_LOG_RECORD_MATCH = PASS
FINAL_PERMISSIVE_RESULT_INVARIANT = PASS_STATIC_SOURCE_SEMANTICS

## Conceptual adversarial cases

A) Direct `HarnessDecision(... PERMIT ...)` -> rejected by public constructor.

B) Direct `HarnessDecision(... AUTHORIZED ...)` -> rejected by public constructor.

C) Direct `LoggedActionResult(permissive_decision, arbitrary_log, None, False)` -> rejected by public constructor.

D) Direct `LoggedActionResult(... log_acknowledged=True ...)` or non-null `log_record` -> rejected by public constructor.

E) Guarded finalizer with same record ID but materially different record -> rejected by exact stored-record equality check.

F) Exact append acknowledgement plus exact matching context remains structurally capable of producing the final result through the private guarded path, subject to all pre-existing authority gates.

## Regression check

D1_REGRESSION_FOUND = FALSE
D2_REGRESSION_FOUND = FALSE
D3_REGRESSION_FOUND = FALSE
D4_REGRESSION_FOUND = FALSE
OTHER_MATERIAL_REGRESSION_FOUND = FALSE

D1 trusted-root closure remains intact: the current trusted execution-policy root remains absent/non-permissive, and authority-bearing assessments continue through trusted-root resolution before permission.

D2 provenance closure remains intact: exact provenance contract/digest semantics were not materially altered by this residual repair.

D3 exact recipient authorization remains intact: output release continues to require exact actor-role authorization separately from cumulative disclosure.

D4 independent approver rule remains intact: when approval is REQUIRED, release actor identity must differ from recipient identity and existing role/action/authority/state checks remain required.

ResourceBoundaryState.WITHIN_AUTHORITY is restored to exact value `WITHIN_AUTHORITY` at the audited target.

Exact input/output manifest canonical binding remains present. Exact cumulative-disclosure tuple `output_id + recipient_actor_id + recipient_role`, empty-ledger UNRESOLVED behavior, and global BLOCKED precedence remain unchanged. Role/action/execution-authority/authorization-state mismatch denial remains unchanged.

No wall-clock access, randomness, environment-derived authority, network access, filesystem write, credential logic, or new external-service behavior was introduced by the residual repair.

## Scope

SCOPE_COMPLIANCE = PASS

Exact comparison:

BASE = d1447fd515e814a21e34118d0a0b063a44220bbd
HEAD = 2bc718711d507b38176981c2b3e55dd607c9547b

shows Builder changes confined to:

- research/weather_forward/v4/a2_harness/contract.py
- research/weather_forward/v4/a2_harness/harness.py

No Owner, Astra, Blue, src, fixture, Gate-B/history, or unrelated Builder mutation is present in this comparison.

## Evidence limits

CODE_EXECUTED = NO
TESTS_RUN = NO
FIXTURES_ACCESSED = NONE
REAL_DATA_ACCESSED = NONE
REAL_METADATA_ACCESSED = NONE
ENDPOINTS_QUERIED = NONE
CREDENTIALS_USED = NONE

RUNTIME_CONTROL_EFFECTIVENESS_VERIFIED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0

AUDIT_VERDICT = PASS_FOR_OWNER_CONSIDERATION_OF_BOUNDED_TEST_AUTHORITY
NEXT_SAFE_ACTION = OWNER_MAY_CONSIDER_BOUNDED_OFFLINE_TEST_AUTHORITY
