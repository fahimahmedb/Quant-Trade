# ASTRA — WEATHER V4 A2 DEDICATED HARNESS STATIC AUDIT — 2026-10-04

AUDIT_BRANCH = astra/weather-v4-a2-dedicated-harness-static-audit-2026-10-04
AUDIT_PARENT_SHA = 649be59e69d8e0724d61352cc76abcac7f3f588e
AUDIT_TARGET_SHA = 649be59e69d8e0724d61352cc76abcac7f3f588e

MISSION_CLASS = INDEPENDENT_ADVERSARIAL_STATIC_AUDIT_WEATHER_V4_A2_DEDICATED_HARNESS

MANDATORY_OWNER_CONSTRUCTION_AUTHORITY = 37e3b25f17a7c5d3b3bc8d37df730aa988585b6c
MANDATORY_BLUE_DESIGN_BASIS = 9b65151c6840cff9d6cad4b6ba897e329862d292

OWNER_AUTHORITY_VERIFIED = TRUE
BLUE_DESIGN_BASIS_VERIFIED = TRUE
BUILDER_HEAD_VERIFIED = TRUE
BUILDER_LINEAGE_VERIFIED = TRUE

Builder branch exact HEAD was verified at 649be59e69d8e0724d61352cc76abcac7f3f588e. Owner authority 37e3b25f17a7c5d3b3bc8d37df730aa988585b6c descends from Blue design basis 9b65151c6840cff9d6cad4b6ba897e329862d292. Builder target is four commits ahead of Owner with the Owner SHA as merge base and no divergence.

## Files reviewed

- research/weather_forward/v4/a2_harness/__init__.py @ 649be59e69d8e0724d61352cc76abcac7f3f588e
- research/weather_forward/v4/a2_harness/contract.py @ 649be59e69d8e0724d61352cc76abcac7f3f588e
- research/weather_forward/v4/a2_harness/harness.py @ 649be59e69d8e0724d61352cc76abcac7f3f588e
- research/weather_forward/v4/a2_harness/README.md @ 649be59e69d8e0724d61352cc76abcac7f3f588e
- research/weather_forward/v4/owner/OWNER_V4_A2_DEDICATED_HARNESS_BUILDER_DECISION_2026-10-04.md @ 37e3b25f17a7c5d3b3bc8d37df730aa988585b6c
- research/weather_forward/v4/blue/BLUE_V4_A2_HARNESS_SUITABILITY_ASSESSMENT_2026-10-04.md @ 9b65151c6840cff9d6cad4b6ba897e329862d292
- research/weather_forward/v4/blue/BLUE_V4_STRUCTURAL_PRE_OPERATIONAL_CONTRACT_2026-10-04.md as inherited at Owner authority
- research/weather_forward/v4/owner/OWNER_OD04_OD12_STRUCTURAL_DECISION_2026-10-04.md as inherited at Owner authority

## Static findings

AUTHORITY_BINDING = REPAIR_REQUIRED
EXACT_INPUT_MANIFEST_BINDING = PASS_INTERNAL_CANONICALIZATION_WITH_AUTHORITY_ROOT_DEFECT
EXACT_OUTPUT_MANIFEST_BINDING = PASS_INTERNAL_CANONICALIZATION_WITH_AUTHORITY_ROOT_DEFECT
INPUT_FAIL_CLOSED_SEMANTICS = REPAIR_REQUIRED
FIXTURE_PROVENANCE_LINEAGE = REPAIR_REQUIRED
ROLE_AUTHORIZATION_SEPARATION = PASS_FOR_ACTOR_ROLE_ACTION_AUTHORITY_STATE_MISMATCHES; DOES_NOT_CURE_TRUST_ROOT_DEFECT
OUTPUT_RELEASE_RESTRICTION = REPAIR_REQUIRED
CUMULATIVE_DISCLOSURE_EXACT_RECIPIENT = PASS_STATIC_TUPLE_MATCHING_AND_BLOCKED_PRECEDENCE
LOGGING_SEMANTICS = REPAIR_REQUIRED_INTERFACE_ONLY
QUARANTINE_STOP_SEMANTICS = PASS_STATIC_FAIL_CLOSED_PATHS_REVIEWED
STATIC_DETERMINISM = PASS_SOURCE_LEVEL_ONLY
SCOPE_COMPLIANCE = PASS

### Manifest canonicalization

The input and output canonical digests include every field present in their respective manifest dataclasses. `manifest_kind` separates input and output domains. JSON keys are sorted, compact separators are fixed, enum values are serialized explicitly, and set-like role/field tuples are sorted before hashing. Duplicate tuple entries remain represented in the serialized array rather than being silently deduplicated, so duplicate insertion changes the digest. No material manifest dataclass field was found omitted from its digest.

This establishes deterministic structural identity relative to the expected identities supplied by policy. It does not establish that the policy itself is an independently trusted Owner artifact; see D1.

### Cumulative disclosure

`CumulativeDisclosureLedger.evaluate()` preserves BLOCKED precedence over unresolved identity/state. Empty history is UNRESOLVED. `evaluate_for()` requires an exact match on `output_id + recipient_actor_id + recipient_role`; a CLEAR record for another actor sharing the same role or for another output cannot by itself satisfy the exact-context check. Unrelated BLOCKED/UNRESOLVED history conservatively blocks rather than permissively clearing release.

This finding concerns tuple-matching semantics only. It is not runtime verification of ledger provenance or tamper resistance.

## Material defects

MATERIAL_DEFECT_COUNT = 5

### D1 — HIGH — Caller-controlled policy is not anchored to an independently trusted Owner root

SOURCE_LOCATION:
- research/weather_forward/v4/a2_harness/harness.py — `HarnessPolicy` definition, approximately lines 45-56.
- research/weather_forward/v4/a2_harness/harness.py — `validate_policy()` and `validate_authority()`, approximately lines 193-271.
- research/weather_forward/v4/a2_harness/harness.py — `A2Harness.validate_binding()` and all permit paths that depend on it.

SEMANTIC_FAILURE_MODE:
`HarnessPolicy` is a public caller-supplied object. `validate_policy()` validates shape and internal class constraints, while `validate_authority()` only compares `AuthorityBinding` fields against the expected values supplied by that same policy. There is no immutable or independently verified root binding the policy itself to a specific Owner authorization artifact, harness identity/version, or manifest contract. Therefore a caller can choose an arbitrary well-formed 40-hex Owner SHA, matching arbitrary harness/version/manifest identities, construct matching manifests, and pass the authority comparison. The code fails closed on disagreement between policy and binding, but not on coordinated substitution of both objects.

This also means `owner_approval_required` is only declarative unless the external policy source is independently established as Owner-approved.

MINIMAL_REPAIR_REQUIREMENT:
Introduce an independently anchored execution-policy root that cannot be substituted by the same caller supplying the decision inputs. Until a future exact Owner execution authority exists, the harness should have no permissive root. A later separately authorized repair may bind an immutable/verified Owner policy identity and exact harness/version/manifest contract, with all permit paths denying if that root is absent or mismatched.

### D2 — HIGH — Fixture provenance/lineage admission is not exact-bound and cannot detect incomplete reproducibility metadata

SOURCE_LOCATION:
- research/weather_forward/v4/a2_harness/contract.py — `FixtureProvenance`.
- research/weather_forward/v4/a2_harness/harness.py — `validate_fixture_provenance()`, approximately lines 372-422.
- research/weather_forward/v4/a2_harness/harness.py — `evaluate_fixture_metadata_admission()`.

SEMANTIC_FAILURE_MODE:
The validator checks only that fixture/generator strings are nonempty/non-ambiguous, lineage references are nonempty, reproducibility metadata contains at least one nonempty unique key/value pair, contamination is CLEAR, admissibility is ADMISSIBLE, and construction classes are allowed. It does not bind fixture ID, generator identity/version, lineage references, or the complete required reproducibility key set to an exact Owner-approved fixture-provenance identity/schema. A metadata object containing only an arbitrary pair such as one nonempty key/value can therefore be structurally admitted even when materially incomplete. Likewise arbitrary nonempty lineage/generator identities can pass.

MINIMAL_REPAIR_REQUIREMENT:
Add an exact canonical fixture-provenance identity or exact Owner-approved provenance schema to policy, covering fixture ID, generator identity/version, complete required lineage, required reproducibility keys/values, contamination/admissibility state, and construction classes. Reject missing required keys, unexpected ambiguity, duplicate lineage where semantically invalid, and any provenance digest mismatch.

### D3 — HIGH — Output recipient authorization is role-bound but not Owner-bound to an exact recipient actor identity

SOURCE_LOCATION:
- research/weather_forward/v4/a2_harness/contract.py — `OutputManifest.permitted_recipients`, approximately lines 155-169.
- research/weather_forward/v4/a2_harness/contract.py — `DisclosureRecord` / `CumulativeDisclosureLedger`.
- research/weather_forward/v4/a2_harness/harness.py — `evaluate_output_release()`, approximately lines 545-628.

SEMANTIC_FAILURE_MODE:
The output manifest allowlist contains roles only. Release verifies that the recipient actor ID is nonempty/non-ambiguous and that cumulative-disclosure history is CLEAR for the exact actor/output/role tuple, but there is no Owner-approved exact recipient actor allowlist or recipient-specific authorization. Cumulative-disclosure safety is not recipient permission. Consequently a new arbitrary actor ID holding an allowed role can become structurally releasable once a CLEAR disclosure record is supplied for that tuple, even though that actor identity was never bound into the approved output manifest/release contract.

This prevents the current schema from representing future exact custody actors/release permissions when those are resolved by Owner authority.

MINIMAL_REPAIR_REQUIREMENT:
Bind exact permitted recipient actor identities, or an exact Owner-approved actor-to-role recipient map, into the output release contract and include it in the output manifest identity. Release must require both exact actor authorization and role authorization; cumulative-disclosure CLEAR remains a separate necessary condition, not a substitute for recipient permission.

### D4 — HIGH — Independent release approval is not enforced against recipient/release-actor identity collapse

SOURCE_LOCATION:
- research/weather_forward/v4/a2_harness/harness.py — `evaluate_output_release()`, approximately lines 545-628.
- research/weather_forward/v4/a2_harness/README.md — output-release description claiming a distinct release actor.
- Owner OD09 / Blue custody contract — independent approval requirement.

SEMANTIC_FAILURE_MODE:
When release approval is REQUIRED, the code requires the release actor to declare `RELEASE_APPROVER` and to hold an AUTHORIZED `RELEASE_OUTPUT` action authorization. It never checks that `release_actor.actor_id != recipient.actor_id`. The same actor can therefore be represented once as recipient and again as release approver and satisfy both paths if the remaining objects match. This contradicts the README's claim of a distinct release actor and does not enforce the upstream independent-approval architecture.

MINIMAL_REPAIR_REQUIREMENT:
For any release requiring independent approval, fail closed unless release actor identity is distinct from recipient identity and satisfies the exact Owner-approved independence rule. Preserve actor/role/action/authority checks in addition to this identity-separation check.

### D5 — MEDIUM — Audit-log schema cannot attribute access/release to an exact actor and append is not a prerequisite to permit

SOURCE_LOCATION:
- research/weather_forward/v4/a2_harness/contract.py — `LogRecord` / `StructuredAuditLog`, approximately lines 200-218.
- research/weather_forward/v4/a2_harness/harness.py — `append_log_record()`, approximately lines 653-675.
- Blue structural contract custody/exposure requirements.

SEMANTIC_FAILURE_MODE:
`LogRecord` stores `actor_role` but not `actor_id`, authorization ID, exact recipient identity, or exact target input/output ID beyond a caller-supplied generic `manifest_identity`. Two different actors sharing a role are indistinguishable in the log. `append_log_record()` is a separate optional operation and permit/release decision paths do not require evidence that an access/release log record was appended. The functional tuple append is immutable in-memory semantics, but it cannot by itself satisfy exact access/exposure attribution and does not establish deployed immutability or tamper-proof logging.

MINIMAL_REPAIR_REQUIREMENT:
Extend log records to bind exact actor identity and the relevant authorization/target context (and exact recipient context for release). Define a fail-closed integration contract under which actions requiring logging cannot be treated as completed without the required append/acknowledgement. Continue to describe the implementation only as in-memory functional append unless a separately verified immutable store exists.

## Non-defects / bounded positive findings

- Wrong/malformed/missing binding values fail closed relative to a fixed trusted policy.
- Actor, role, action, authority-SHA, and authorization-state mismatches fail closed in `validate_role_authorization()`.
- Unknown/prohibited input classes are denied relative to policy; unresolved visibility/permission states are denied.
- Input/output manifest identity mismatches deny.
- Output exportability, quarantine, leakage, manifest cumulative-disclosure state, exact-context disclosure state, and release authorization are all checked before `AUTHORIZED` release.
- Quarantine/STOP paths do not contain a permissive fallback found by static inspection.
- No wall clock, randomness, environment authority, network access, filesystem writes, external services, or credential logic was found in the dedicated harness source.
- Functional log append returns a new tuple-backed value and does not mutate hidden global state.

## Scope audit

Complete comparison from Owner construction authority 37e3b25f17a7c5d3b3bc8d37df730aa988585b6c to Builder target 649be59e69d8e0724d61352cc76abcac7f3f588e shows exactly four added files, all under `research/weather_forward/v4/a2_harness/`:

- README.md
- __init__.py
- contract.py
- harness.py

No file outside the dedicated A2 harness area changed. The historical Gate-B runner `governance/run_gate_b_evidence_schema_discriminants_2026-09-21.py` was not modified.

## Evidence limits and invariants

CODE_EXECUTED = NO
TESTS_RUN = NO
FIXTURES_ACCESSED = NONE
FIXTURES_CREATED = NONE
REAL_DATA_ACCESSED = NONE
REAL_METADATA_ACCESSED = NONE
ENDPOINTS_QUERIED = NONE
CREDENTIALS_USED = NONE

RUNTIME_CONTROL_EFFECTIVENESS_VERIFIED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0

STATIC_SOURCE_PRESENT != SEMANTICALLY_CORRECT
SEMANTICALLY_CORRECT_BY_STATIC_AUDIT != RUNTIME_VERIFIED
RUNTIME_VERIFIED != A2_EXECUTION_AUTHORIZED
ASTRA_PASS != A2_PHASE_AUTHORIZATION

AUDIT_VERDICT = REPAIR_REQUIRED
NEXT_SAFE_ACTION = OWNER_REVIEW_OF_ASTRA_DEFECTS_ONLY
