# OWNER — WEATHER V4 A2 STATIC AUDIT REPAIR DECISION — 2026-10-05

OWNER_AUTHORITY_BASE_SHA =
07405b3c20168014993f1616c19e7d47f5e2a41f

MANDATORY_ASTRA_AUDIT_SHA =
07405b3c20168014993f1616c19e7d47f5e2a41f

MANDATORY_BUILDER_TARGET_SHA =
649be59e69d8e0724d61352cc76abcac7f3f588e

MANDATORY_PRIOR_OWNER_CONSTRUCTION_AUTHORITY =
37e3b25f17a7c5d3b3bc8d37df730aa988585b6c

MISSION_CLASS =
OWNER_AUTHORIZATION_FOR_CONSOLIDATED_STATIC_REPAIR_OF_ASTRA_D1_D5_ONLY

ASTRA_AUDIT_VERDICT =
REPAIR_REQUIRED

ASTRA_MATERIAL_DEFECT_COUNT =
5

BUILDER_AUTHORIZED =
TRUE_FOR_CONSOLIDATED_STATIC_REPAIR_D1_D5_ONLY

AUTONOMY_INSIDE_AUTHORIZED_REPAIR_SCOPE =
MAXIMIZED

AUTHORITY_EXPANSION =
PROHIBITED

## 1. Purpose

This Owner decision authorizes one consolidated Builder repair pass over the dedicated Weather V4 A2 static harness to address Astra defects D1 through D5 from exact audit commit 07405b3c20168014993f1616c19e7d47f5e2a41f.

The Builder should complete all technically resolvable in-scope repairs autonomously and should not return for ordinary design choices.

DESIGN_AMBIGUITY =
BUILDER_DECIDES_CONSERVATIVELY_AND_CONTINUES

AUTHORITY_AMBIGUITY =
BUILDER_STOPS

This artifact authorizes static source construction/repair only.

It does NOT authorize execution, tests, fixtures, real data, real metadata, endpoints, credentials, A2 execution, capture, economics, trading or capital.

## 2. D1 — independently anchored execution-policy root

D1_STATUS =
REPAIR_AUTHORIZED

A caller-supplied HarnessPolicy must not itself constitute the root of trust.

The repaired harness must distinguish:

- construction authority;
- future execution-policy authority;
- caller-supplied decision inputs.

CURRENT_OWNER_EXECUTION_POLICY_AUTHORITY =
NONE

CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT =
NONE

Therefore, under the current governance state:

NO_TRUSTED_EXECUTION_POLICY_ROOT =
DENY_ALL_PERMIT_RELEASE_ADMISSION_PATHS

The Builder is authorized to implement an independently anchored static execution-policy root mechanism or equivalent fail-closed architecture such that the same caller supplying AuthorityBinding / manifests / action inputs cannot substitute the trusted expected root.

The preferred current-state semantic is:

- no permissive execution-policy root exists yet;
- the harness source may contain a non-permissive anchored state indicating that execution authority is absent;
- all would-be permit/release/admission paths must deny while that root is absent;
- a future exact Owner artifact must separately authorize any permissive execution-policy root before A2 execution can ever be considered.

The Builder must NOT fabricate a future execution-policy SHA, policy digest, fixture identity, actor list or execution approval.

A future trusted root may be represented structurally now, but must remain unresolved/non-permissive until separately authorized.

CONSTRUCTION_AUTHORITY_SHA != EXECUTION_POLICY_AUTHORITY

CALLER_SUPPLIED_POLICY != TRUSTED_POLICY_ROOT

ABSENCE_OF_EXECUTION_POLICY_AUTHORITY = FAIL_CLOSED

## 3. D2 — exact fixture provenance / lineage contract

D2_STATUS =
REPAIR_AUTHORIZED

The Builder may extend static structures so that future fixture metadata can be admitted only against exact trusted policy requirements.

The future provenance contract must be able to exact-bind, directly or through deterministic canonical identity, all material fields including at minimum:

- fixture identifier;
- construction input classes;
- generator identity;
- generator version;
- complete required lineage references;
- complete required reproducibility metadata schema / keys / values or exact structural identity;
- contamination state;
- admissibility state.

Arbitrary nonempty strings or a one-pair metadata map must not be sufficient merely because they are nonempty.

The repaired static design must support:

- exact expected provenance identity and/or exact required provenance schema;
- explicit required reproducibility keys;
- rejection of missing required keys;
- rejection of unexpected ambiguity;
- rejection of invalid duplicate lineage when duplicates would alter meaning;
- digest/identity mismatch fail-closed semantics.

CURRENT_APPROVED_FIXTURE_PROVENANCE_IDENTITY =
NONE

CURRENT_FIXTURE_GENERATION_AUTHORIZED =
FALSE

CURRENT_FIXTURE_TESTING_AUTHORIZED =
FALSE

Therefore no real or sample fixture may be created to populate this contract.

## 4. D3 — exact recipient authorization

D3_STATUS =
REPAIR_AUTHORIZED

Role-only recipient authorization is insufficient.

The repaired output-release contract must be able to bind recipient permission to an exact Owner-approved recipient identity model, such as:

- exact permitted recipient actor IDs; or
- an exact actor-to-role authorization map;

and that recipient authorization material must be covered by the trusted execution-policy / output-contract identity used for future execution.

Cumulative-disclosure CLEAR remains a separate necessary condition and must never substitute for recipient authorization.

CURRENT_APPROVED_RECIPIENT_ACTOR_IDS =
NONE

CURRENT_APPROVED_ACTOR_ROLE_MAP =
NONE

Do not invent real actor identities.

Current absence of an exact approved recipient model must fail closed.

## 5. D4 — independent release approval

D4_STATUS =
REPAIR_AUTHORIZED

For any release whose approval requirement is REQUIRED, the minimum structural independence rule is hereby ratified:

MINIMUM_RELEASE_INDEPENDENCE_RULE =
RELEASE_ACTOR_ID_MUST_DIFFER_FROM_RECIPIENT_ACTOR_ID

This minimum rule does not replace any future stronger Owner-approved independence rule.

The repaired harness must fail closed if REQUIRED approval is represented by the same exact actor identity as the recipient.

The release actor must still satisfy all existing actor / role / action / authority / authorization-state checks.

README / source semantics must agree.

## 6. D5 — logging attribution and completion semantics

D5_STATUS =
REPAIR_AUTHORIZED

The static log contract must be extended to carry enough exact context for future attribution.

At minimum, logging must be able to bind:

- exact actor identity;
- actor role;
- relevant authorization identity;
- exact attempted action;
- exact target input/output/fixture or manifest context;
- permit/deny state;
- quarantine state;
- release state;
- incident identity when applicable;
- cumulative-disclosure state when applicable;
- exact recipient actor/role context for release when applicable.

The Builder may choose the smallest auditable representation.

The implementation must also remove the semantic possibility that an action requiring logging is treated as fully completed while no required log append/acknowledgement has occurred.

Authorized repair patterns include, for example:

- atomic evaluate-and-log APIs returning the new immutable log together with the completed decision; or
- explicit PENDING_LOG / NOT_COMPLETED semantics followed by a fail-closed finalization step that verifies the exact required record; or
- another equally strict deterministic offline construction.

The Builder should choose the minimal clear design autonomously.

Logging remains only an in-memory functional/static interface unless separately proven otherwise.

LOG_INTERFACE_IMPLEMENTED != DEPLOYED_IMMUTABILITY

LOG_INTERFACE_IMPLEMENTED != TAMPER_PROOF

## 7. Preserve bounded positive findings

The Builder must preserve, not regress, the Astra-positive findings already established statically, including:

- deterministic input/output manifest canonicalization covering material fields;
- exact recipient cumulative-disclosure tuple semantics;
- BLOCKED precedence over UNRESOLVED/CLEAR;
- actor/role/action/authority/state mismatch denial;
- fail-closed unresolved/blocked authority, manifest, leakage, disclosure, quarantine and resource states;
- static determinism;
- no wall clock;
- no randomness;
- no environment-derived authority;
- no network behavior;
- no filesystem writes;
- no credential logic;
- no external service calls;
- no hidden mutable global state;
- historical Gate-B runner unchanged.

## 8. Builder autonomy

Within this exact repair scope, the Builder is authorized to decide autonomously:

- class / dataclass / enum / protocol structure;
- module-local helper functions;
- canonical serialization details;
- deterministic digest representation;
- trusted-root representation, provided current state remains non-permissive;
- exact static policy schemas;
- logging completion representation;
- internal error / STOP reasons;
- README wording;
- refactors inside research/weather_forward/v4/a2_harness/ required to close D1-D5.

Do not ask Owner to choose between technically equivalent safe implementations.

If an in-scope defect is found during static self-review, fix it autonomously.

## 9. Allowed repository mutation

The Builder may modify only files under:

research/weather_forward/v4/a2_harness/

The Builder may modify the existing dedicated harness files and, if genuinely useful, add minimal new helper modules inside that same directory.

Do NOT modify:

- src/;
- governance/run_gate_b_evidence_schema_discriminants_2026-09-21.py;
- historical fixtures;
- Owner artifacts;
- Blue artifacts;
- Astra audit artifacts;
- unrelated repository files.

## 10. Absolute non-authorizations

BUILDER_IMPLEMENTATION_TEST_EXECUTION =
NOT_AUTHORIZED

CODE_EXECUTION_AUTHORIZED =
FALSE

TEST_EXECUTION_AUTHORIZED =
FALSE

A2_FIXTURE_GENERATION_AUTHORIZED =
FALSE

A2_FIXTURE_TESTING_AUTHORIZED =
FALSE

A2_EXECUTION_AUTHORIZED =
FALSE

REAL_DATA_ACCESS =
NONE

REAL_METADATA_ACCESS =
NONE

ENDPOINT_ACCESS =
NONE

CREDENTIAL_USE =
NONE

CAPTURE_AUTHORIZATION =
NONE

ECONOMIC_AUTHORITY =
0

REAL_CAPITAL_AUTHORIZED =
FALSE

LIVE_TRADING_AUTHORIZED =
FALSE

DATA_T0 =
NOT_DECLARED

EXPERIMENT_T0 =
NOT_DECLARED

The Builder must NOT:

- run Python;
- import the harness;
- run tests / pytest / linters / type checkers / CI;
- generate or inspect fixtures;
- access real data or real metadata;
- query endpoints;
- use credentials;
- choose operational sources/stations/cities/models;
- perform backtests, PnL or economic analysis;
- activate A2;
- create a permissive execution-policy root without a separate future Owner execution authority.

## 11. Hard STOP boundary

Builder should STOP only if closing D1-D5 genuinely requires authority outside this artifact.

Examples:

- actual fixture generation/inspection;
- execution/testing;
- real actor identity assignment;
- real execution-policy approval;
- real endpoint/credential use;
- operational source selection;
- src/ modification;
- historical Gate-B runner modification;
- economic assumptions;
- any future A2 phase activation.

If the missing item is only a future value, the Builder should prefer implementing a fail-closed unresolved/none state and continue static construction rather than stopping.

## 12. Completion standard

The repair is complete only when source-level semantics address D1-D5 and a static self-review finds no known in-scope material defect left unfixed.

Successful repair meaning:

ASTRA_D1_D5_STATIC_REPAIR_IMPLEMENTATION_COMPLETE

This does NOT mean:

- runtime verified;
- control effectiveness verified;
- A2 approved;
- A2 execution ready;
- fixture approved;
- trusted execution policy approved;
- real data access approved;
- economic authority granted.

## 13. Required Builder handoff

Return at minimum:

BRANCH
COMMIT_SHA
PARENT_SHA
OWNER_REPAIR_AUTHORITY_VERIFIED
ASTRA_AUDIT_SHA_VERIFIED
FILES_MODIFIED
FILES_CREATED
FILES_MODIFIED_OUTSIDE_SCOPE

D1_TRUSTED_EXECUTION_POLICY_ROOT_REPAIRED
CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT
NO_ROOT_DENY_ALL_ENFORCED

D2_EXACT_FIXTURE_PROVENANCE_CONTRACT_REPAIRED
CURRENT_APPROVED_FIXTURE_PROVENANCE_IDENTITY

D3_EXACT_RECIPIENT_AUTHORIZATION_REPAIRED
CURRENT_APPROVED_RECIPIENT_ACTOR_IDS

D4_RELEASE_RECIPIENT_INDEPENDENCE_REPAIRED
MINIMUM_RELEASE_INDEPENDENCE_RULE

D5_LOG_EXACT_ATTRIBUTION_REPAIRED
D5_LOG_REQUIRED_FOR_COMPLETION_REPAIRED

POSITIVE_FINDINGS_REGRESSION_FOUND
KNOWN_IN_SCOPE_DEFECTS_LEFT_UNFIXED
STATIC_SELF_REVIEW_COMPLETE

HISTORICAL_GATE_B_RUNNER_MODIFIED
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

Expected successful invariants:

FILES_MODIFIED_OUTSIDE_SCOPE = NONE
D1_TRUSTED_EXECUTION_POLICY_ROOT_REPAIRED = TRUE
CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT = NONE
NO_ROOT_DENY_ALL_ENFORCED = TRUE
D2_EXACT_FIXTURE_PROVENANCE_CONTRACT_REPAIRED = TRUE
CURRENT_APPROVED_FIXTURE_PROVENANCE_IDENTITY = NONE
D3_EXACT_RECIPIENT_AUTHORIZATION_REPAIRED = TRUE
CURRENT_APPROVED_RECIPIENT_ACTOR_IDS = NONE
D4_RELEASE_RECIPIENT_INDEPENDENCE_REPAIRED = TRUE
MINIMUM_RELEASE_INDEPENDENCE_RULE = RELEASE_ACTOR_ID_MUST_DIFFER_FROM_RECIPIENT_ACTOR_ID
D5_LOG_EXACT_ATTRIBUTION_REPAIRED = TRUE
D5_LOG_REQUIRED_FOR_COMPLETION_REPAIRED = TRUE
POSITIVE_FINDINGS_REGRESSION_FOUND = FALSE
KNOWN_IN_SCOPE_DEFECTS_LEFT_UNFIXED = NONE
STATIC_SELF_REVIEW_COMPLETE = TRUE
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
CAPTURE_AUTHORIZATION = NONE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED

TERMINAL_STATE =
ASTRA_D1_D5_STATIC_REPAIR_IMPLEMENTATION_COMPLETE

NEXT_SAFE_ACTION =
ASTRA_INDEPENDENT_STATIC_RECHECK_ONLY
