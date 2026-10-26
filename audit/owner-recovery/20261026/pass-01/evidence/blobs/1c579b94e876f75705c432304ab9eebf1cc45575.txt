# ASTRA — WEATHER V4 A2 D1–D5 STATIC RECHECK — 2026-10-05

AUDIT_BRANCH = astra/weather-v4-a2-d1-d5-static-recheck-2026-10-05
AUDIT_PARENT_SHA = fa81d3fbddca2802e43ea0b05fe85e608b98a61d
AUDIT_TARGET_SHA = fa81d3fbddca2802e43ea0b05fe85e608b98a61d

MISSION_CLASS = INDEPENDENT_ADVERSARIAL_STATIC_RECHECK_WEATHER_V4_A2_ASTRA_D1_D5_REPAIR

MANDATORY_OWNER_REPAIR_AUTHORITY = 08b40c41bdadb05b572a88fc1279310c436d32f7
MANDATORY_PRIOR_ASTRA_AUDIT = 07405b3c20168014993f1616c19e7d47f5e2a41f
PRIOR_AUDITED_BUILDER_TARGET = 649be59e69d8e0724d61352cc76abcac7f3f588e

OWNER_REPAIR_AUTHORITY_VERIFIED = TRUE
PRIOR_ASTRA_AUDIT_VERIFIED = TRUE
BUILDER_LINEAGE_VERIFIED = TRUE

Required lineage resolved exactly:

07405b3c20168014993f1616c19e7d47f5e2a41f
-> 08b40c41bdadb05b572a88fc1279310c436d32f7
-> fa81d3fbddca2802e43ea0b05fe85e608b98a61d

The Builder repair branch exact HEAD was verified at fa81d3fbddca2802e43ea0b05fe85e608b98a61d.

## Files reviewed

- research/weather_forward/v4/a2_harness/__init__.py @ fa81d3fbddca2802e43ea0b05fe85e608b98a61d
- research/weather_forward/v4/a2_harness/contract.py @ fa81d3fbddca2802e43ea0b05fe85e608b98a61d
- research/weather_forward/v4/a2_harness/harness.py @ fa81d3fbddca2802e43ea0b05fe85e608b98a61d
- research/weather_forward/v4/a2_harness/trusted_root.py @ fa81d3fbddca2802e43ea0b05fe85e608b98a61d
- research/weather_forward/v4/a2_harness/README.md @ fa81d3fbddca2802e43ea0b05fe85e608b98a61d
- research/weather_forward/v4/owner/OWNER_V4_A2_STATIC_AUDIT_REPAIR_DECISION_2026-10-05.md @ 08b40c41bdadb05b572a88fc1279310c436d32f7
- research/weather_forward/v4/audit/ASTRA_V4_A2_DEDICATED_HARNESS_STATIC_AUDIT_2026-10-04.md @ 07405b3c20168014993f1616c19e7d47f5e2a41f

## D1 recheck — trusted execution-policy root

D1_STATUS = CLOSED

`trusted_root.py` contains the current source-anchored non-permissive state. `get_trusted_execution_policy_root()` takes no caller input and returns `None`; no active-root setter or caller-supplied constructor path is used by the harness. `HarnessPolicy` remains caller supplied, but all authority-bearing action assessments resolve the independently imported trusted root before permission logic. With the current root absent, input read, fixture admission, output release, and resource-boundary validation cannot reach a positive authority-bearing result through the action APIs.

The future `TrustedExecutionPolicyRoot` structure distinguishes `execution_policy_authority_sha` from `expected_construction_authority_sha` and binds exact harness identity/version plus exact deterministic `HarnessPolicy` identity. The policy identity covers input/output manifest identities, class sets, fixture provenance contract, and exact recipient actor-role map. `ActionAuthorization.authority_sha` is checked against the execution-policy authority, not construction authority.

Coordinated caller substitution of `HarnessPolicy + AuthorityBinding` therefore no longer creates a valid authority universe under the current source semantics.

CURRENT_OWNER_EXECUTION_POLICY_AUTHORITY = NONE
CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT = NONE
NO_ROOT_DENY_ALL_ENFORCED = TRUE_FOR_AUTHORITY_BEARING_ACTION_APIS

## D2 recheck — exact fixture provenance / lineage

D2_STATUS = CLOSED

Fixture provenance now has a deterministic structural identity covering fixture ID, construction input classes, generator identity/version, lineage references, reproducibility metadata keys and values, contamination state, and admissibility state.

`FixtureProvenanceContract` exact-binds expected fixture ID, generator identity/version, construction classes, lineage references, required/allowed reproducibility keys, and exact provenance digest. Validation rejects empty/ambiguous identities, duplicate construction classes, duplicate lineage, duplicate metadata keys, missing required keys, unexpected keys, wrong fixture/generator/version/classes/lineage, UNKNOWN or contaminated state, non-admissible state, and digest mismatch.

A one-key reproducibility map cannot satisfy a contract requiring additional keys, and arbitrary nonempty provenance cannot become admission authority.

Current fixture admission remains non-permissive because no trusted execution-policy root exists; additionally, a policy with no fixture provenance contract is explicitly blocked.

CURRENT_APPROVED_FIXTURE_PROVENANCE_IDENTITY = NONE

## D3 recheck — exact recipient authorization

D3_STATUS = CLOSED

Recipient authorization is no longer role-only. `HarnessPolicy.permitted_recipient_actor_roles` exact-binds actor ID to role and is covered by `harness_policy_identity()`, which a future trusted root must exact-bind. Duplicate recipient actor IDs are rejected at policy validation and ambiguous actor IDs are blocked.

Release requires both recipient role membership in the output manifest and exact `(recipient.actor_id, recipient.declared_role)` membership in the policy map. Cumulative-disclosure CLEAR remains a separate condition and cannot substitute for recipient permission.

With the current trusted root absent, release remains impossible even if a caller supplies a fabricated actor map and CLEAR disclosure record.

CURRENT_APPROVED_RECIPIENT_ACTOR_IDS = NONE
CURRENT_APPROVED_ACTOR_ROLE_MAP = NONE

## D4 recheck — independent release approver

D4_STATUS = CLOSED

For `release_approval_requirement = REQUIRED`, source explicitly rejects missing/ambiguous release actor identity and rejects `release_actor.actor_id == recipient.actor_id` with `RELEASE_INDEPENDENCE_VIOLATION`.

The existing checks remain additive: exact release actor identity, `RELEASE_APPROVER` role, `RELEASE_OUTPUT` action, authorization authority equal to trusted execution-policy authority, and `AUTHORIZED` authorization state.

MINIMUM_RELEASE_INDEPENDENCE_RULE = RELEASE_ACTOR_ID_MUST_DIFFER_FROM_RECIPIENT_ACTOR_ID

## D5 recheck — logging attribution and completion

D5_STATUS = STILL_OPEN

The attribution half of D5 is repaired. `LogRecord` now carries exact construction authority, execution-policy authority, authorization authority, actor ID, actor role, authorization ID, attempted action, target kind, target ID, manifest/provenance identity, permit/deny state, quarantine state, release state, incident ID, cumulative-disclosure state, and release recipient actor/role. Two actors sharing a role are distinguishable.

The action-API completion flow is also substantially repaired. `_assess_*` methods are private eligibility assessments. Public `evaluate_input_read`, `evaluate_fixture_metadata_admission`, and `evaluate_output_release` route through `_complete_with_required_log()`. Missing/ambiguous or duplicate log record IDs and failed append acknowledgement yield `DENY`, `BLOCKED`, `NOT_COMPLETED`, `LOGGING_REQUIRED`. A successful append acknowledgement occurs before those action APIs construct a completed permissive decision.

However, the repair does not close the explicit direct-constructor bypass required by this recheck mandate.

SOURCE LOCATIONS:
- research/weather_forward/v4/a2_harness/contract.py — public dataclasses `HarnessDecision` and `LoggedActionResult`.
- research/weather_forward/v4/a2_harness/__init__.py — both classes are publicly re-exported.

SEMANTIC FAILURE MODE:
`HarnessDecision` has no `__post_init__`, factory restriction, acknowledgement token, or other invariant preventing direct construction of:

- `permit_or_deny_state = PERMIT`;
- `release_state = AUTHORIZED`;
- `completion_state = COMPLETED`;

without any successful log append or acknowledgement.

`LoggedActionResult` is likewise publicly constructible and does not enforce the invariant that a permissive/completed decision requires `log_acknowledged = True` plus a corresponding exact `log_record` actually present in `log`.

Therefore an external caller can construct a semantically final permissive result object directly without using the required evaluate-and-log path. This is a public source-level route producing the exact final states the repair intended to reserve for acknowledged logging.

This does not mean the three `evaluate_*` methods are permissive before logging; they are not. It means the public final-state model itself still permits unlogged final `PERMIT/AUTHORIZED`, so the required implication is not globally enforced:

FINAL_PERMIT_OR_AUTHORIZED
=> REQUIRED_LOG_ACKNOWLEDGED

MINIMAL_REPAIR_REQUIREMENT:
Make final permissive/completed decision construction enforce the logging invariant at the type/factory boundary. For example, keep raw assessment/internal decision types private and expose final `HarnessDecision` / `LoggedActionResult` only through a guarded factory requiring a successful exact append acknowledgement, or add construction invariants that reject any `PERMIT`/`AUTHORIZED`/`COMPLETED` combination unless the exact acknowledged log record is cryptographically or structurally linked to the returned log/result. The repair need not provide deployed tamper-proof storage.

Logging remains correctly described as in-memory functional immutable-value semantics only, not deployed immutable or tamper-proof storage.

## Regression audit

EXACT_INPUT_MANIFEST_BINDING = PASS_NO_MATERIAL_REGRESSION
EXACT_OUTPUT_MANIFEST_BINDING = PASS_NO_MATERIAL_REGRESSION
CUMULATIVE_DISCLOSURE_EXACT_RECIPIENT = PASS_NO_MATERIAL_REGRESSION
BLOCKED_PRECEDENCE = PASS_NO_MATERIAL_REGRESSION
ROLE_ACTION_AUTHORITY_FAIL_CLOSED = PASS_NO_MATERIAL_REGRESSION
STATIC_DETERMINISM = PASS_SOURCE_LEVEL_ONLY

Input and output canonical digests still cover all material fields present in their respective manifest dataclasses. Set-like tuples are sorted without silent deduplication.

Cumulative disclosure still requires exact `output_id + recipient_actor_id + recipient_role`; empty ledger remains `UNRESOLVED`; global `BLOCKED` retains precedence over unresolved/clear history.

Actor, role, action, execution-policy authority, and authorization-state mismatches fail closed. Unresolved visibility/permission/leakage/quarantine/resource states remain non-permissive through the authority-bearing APIs.

No wall clock, randomness, environment-derived authority, network access, credential logic, filesystem writes, external-service calls, or hidden mutable global state were found in the reviewed dedicated harness source.

## Scope audit

SCOPE_COMPLIANCE = PASS

Exact comparison:

BASE = 08b40c41bdadb05b572a88fc1279310c436d32f7
HEAD = fa81d3fbddca2802e43ea0b05fe85e608b98a61d

shows only:

- research/weather_forward/v4/a2_harness/README.md — modified
- research/weather_forward/v4/a2_harness/__init__.py — modified
- research/weather_forward/v4/a2_harness/contract.py — modified
- research/weather_forward/v4/a2_harness/harness.py — modified
- research/weather_forward/v4/a2_harness/trusted_root.py — added

No Owner, Astra, Blue, src, governance, historical fixture, Gate-B runner, or unrelated file was changed by the Builder repair.

Historical Gate-B runner remains unchanged by this repair.

## New defect assessment

NEW_MATERIAL_DEFECT_COUNT = 0

No distinct new material defect caused by the repair was identified. The direct-constructor issue is classified as residual D5 because the recheck mandate explicitly required direct-constructor analysis under D5 logging-completion semantics.

## Evidence limits and invariants

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

D1_STATUS = CLOSED
D2_STATUS = CLOSED
D3_STATUS = CLOSED
D4_STATUS = CLOSED
D5_STATUS = STILL_OPEN

AUDIT_VERDICT = REPAIR_REQUIRED
NEXT_SAFE_ACTION = OWNER_REVIEW_OF_ASTRA_RECHECK_DEFECTS_ONLY
