from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

from .contract import (
    Action,
    ActionAuthorization,
    AdmissibilityState,
    AuthorityBinding,
    AuthorizationState,
    CompletionState,
    ContaminationState,
    CumulativeDisclosureLedger,
    CumulativeDisclosureState,
    FixtureProvenance,
    FixtureProvenanceContract,
    HarnessDecision,
    InputClassification,
    InputManifest,
    LeakageAssessment,
    LoggedActionResult,
    LogRecord,
    OutputManifest,
    PermissionState,
    PermitState,
    QuarantineState,
    ReleaseState,
    RequirementState,
    ResourceBoundaryState,
    Role,
    RoleDeclaration,
    StopReason,
    StructuredAuditLog,
    TargetKind,
    TrustedExecutionPolicyRoot,
    ValidationResult,
    ValidationState,
    VisibilityState,
    _finalize_logged_action_result,
)
from .trusted_root import get_trusted_execution_policy_root


_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256_IDENTITY = re.compile(r"^sha256:[0-9a-f]{64}$")
_AMBIGUOUS_TOKENS = frozenset({"UNKNOWN", "UNRESOLVED", "AMBIGUOUS", "NOT_ATTESTED", "NONE"})


@dataclass(frozen=True, slots=True)
class HarnessPolicy:
    expected_owner_authority_sha: str
    expected_harness_identity: str
    expected_harness_version_or_commit_identity: str
    expected_manifest_version_identity: str
    expected_input_manifest_id: str
    expected_input_manifest_identity: str
    expected_output_manifest_id: str
    expected_output_manifest_identity: str
    allowed_input_classifications: tuple[InputClassification, ...]
    prohibited_input_classifications: tuple[InputClassification, ...]
    fixture_provenance_contract: FixtureProvenanceContract | None
    permitted_recipient_actor_roles: tuple[tuple[str, Role], ...]


@dataclass(frozen=True, slots=True)
class _ActionAssessment:
    allowed: bool
    release_authorized: bool
    quarantine_state: QuarantineState
    stop_reason: StopReason | None
    detail_code: str
    cumulative_disclosure_state: CumulativeDisclosureState | None = None


def _blocked(reason: StopReason, detail_code: str) -> ValidationResult:
    return ValidationResult(ValidationState.BLOCKED, reason, detail_code)


def _invalid(reason: StopReason, detail_code: str) -> ValidationResult:
    return ValidationResult(ValidationState.INVALID, reason, detail_code)


def _valid(detail_code: str) -> ValidationResult:
    return ValidationResult(ValidationState.VALID, None, detail_code)


def _assessment_deny(
    reason: StopReason,
    detail_code: str,
    quarantine_state: QuarantineState = QuarantineState.BLOCKED_PENDING_OWNER_REVIEW,
    cumulative_disclosure_state: CumulativeDisclosureState | None = None,
) -> _ActionAssessment:
    return _ActionAssessment(
        allowed=False,
        release_authorized=False,
        quarantine_state=quarantine_state,
        stop_reason=reason,
        detail_code=detail_code,
        cumulative_disclosure_state=cumulative_disclosure_state,
    )


def _assessment_allow(
    detail_code: str,
    release_authorized: bool,
    cumulative_disclosure_state: CumulativeDisclosureState | None = None,
) -> _ActionAssessment:
    return _ActionAssessment(
        allowed=True,
        release_authorized=release_authorized,
        quarantine_state=QuarantineState.CLEAR,
        stop_reason=None,
        detail_code=detail_code,
        cumulative_disclosure_state=cumulative_disclosure_state,
    )


def _logging_failure(detail_code: str) -> HarnessDecision:
    return HarnessDecision(
        validation_state=ValidationState.BLOCKED,
        permit_or_deny_state=PermitState.DENY,
        quarantine_state=QuarantineState.BLOCKED_PENDING_OWNER_REVIEW,
        release_state=ReleaseState.BLOCKED,
        completion_state=CompletionState.NOT_COMPLETED,
        stop_reason=StopReason.LOGGING_REQUIRED,
        detail_code=detail_code,
    )


def _nonempty(value: str) -> bool:
    return bool(value and value.strip())


def _ambiguous(value: str) -> bool:
    return value.strip().upper() in _AMBIGUOUS_TOKENS


def _resolved_identity(value: str) -> bool:
    return _nonempty(value) and not _ambiguous(value)


def _has_wildcard(values: tuple[str, ...]) -> bool:
    return any("*" in value for value in values)


def _canonical_digest(payload: dict[str, object]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def input_manifest_identity(manifest: InputManifest) -> str:
    return _canonical_digest(
        {
            "manifest_kind": "InputManifest",
            "input_id": manifest.input_id,
            "manifest_version_identity": manifest.manifest_version_identity,
            "input_classification": manifest.input_classification.value,
            "source_provenance_class": manifest.source_provenance_class,
            "exact_permitted_fields": sorted(manifest.exact_permitted_fields),
            "exact_prohibited_fields": sorted(manifest.exact_prohibited_fields),
            "permitted_reader_roles": sorted(role.value for role in manifest.permitted_reader_roles),
            "raw_values_visible": manifest.raw_values_visible.value,
            "timestamps_visible": manifest.timestamps_visible.value,
            "frequency_or_count_information_visible": manifest.frequency_or_count_information_visible.value,
            "longitudinal_observation_allowed": manifest.longitudinal_observation_allowed.value,
            "aggregation_allowed": manifest.aggregation_allowed.value,
            "cross_source_comparison_allowed": manifest.cross_source_comparison_allowed.value,
            "efficacy_leakage_assessment": manifest.efficacy_leakage_assessment.value,
            "access_logging_requirement": manifest.access_logging_requirement.value,
            "quarantine_on_ambiguity": manifest.quarantine_on_ambiguity.value,
            "owner_approval_required": manifest.owner_approval_required.value,
        }
    )


def output_manifest_identity(manifest: OutputManifest) -> str:
    return _canonical_digest(
        {
            "manifest_kind": "OutputManifest",
            "output_id": manifest.output_id,
            "manifest_version_identity": manifest.manifest_version_identity,
            "output_type": manifest.output_type,
            "exact_metric_or_artifact": manifest.exact_metric_or_artifact,
            "granularity": manifest.granularity,
            "permitted_recipients": sorted(role.value for role in manifest.permitted_recipients),
            "exportability": manifest.exportability.value,
            "quarantine_status": manifest.quarantine_status.value,
            "cumulative_disclosure_risk": manifest.cumulative_disclosure_risk.value,
            "efficacy_leakage_assessment": manifest.efficacy_leakage_assessment.value,
            "release_approval_requirement": manifest.release_approval_requirement.value,
            "retention_rule": manifest.retention_rule,
            "incident_if_unexpected_information_revealed": manifest.incident_if_unexpected_information_revealed,
        }
    )


def fixture_provenance_identity(provenance: FixtureProvenance) -> str:
    return _canonical_digest(
        {
            "contract_kind": "FixtureProvenance",
            "fixture_id": provenance.fixture_id,
            "construction_input_classes": sorted(item.value for item in provenance.construction_input_classes),
            "generator_identity": provenance.generator_identity,
            "generator_version": provenance.generator_version,
            "lineage_references": sorted(provenance.lineage_references),
            "reproducibility_metadata": sorted(
                [[key, value] for key, value in provenance.reproducibility_metadata],
                key=lambda item: (item[0], item[1]),
            ),
            "contamination_state": provenance.contamination_state.value,
            "admissibility_state": provenance.admissibility_state.value,
        }
    )


def _fixture_contract_payload(contract: FixtureProvenanceContract | None) -> object:
    if contract is None:
        return None
    return {
        "expected_fixture_id": contract.expected_fixture_id,
        "expected_generator_identity": contract.expected_generator_identity,
        "expected_generator_version": contract.expected_generator_version,
        "expected_construction_input_classes": sorted(
            item.value for item in contract.expected_construction_input_classes
        ),
        "expected_lineage_references": sorted(contract.expected_lineage_references),
        "required_reproducibility_keys": sorted(contract.required_reproducibility_keys),
        "allowed_reproducibility_keys": sorted(contract.allowed_reproducibility_keys),
        "expected_fixture_provenance_identity": contract.expected_fixture_provenance_identity,
    }


def harness_policy_identity(policy: HarnessPolicy) -> str:
    return _canonical_digest(
        {
            "contract_kind": "HarnessPolicy",
            "expected_owner_authority_sha": policy.expected_owner_authority_sha,
            "expected_harness_identity": policy.expected_harness_identity,
            "expected_harness_version_or_commit_identity": policy.expected_harness_version_or_commit_identity,
            "expected_manifest_version_identity": policy.expected_manifest_version_identity,
            "expected_input_manifest_id": policy.expected_input_manifest_id,
            "expected_input_manifest_identity": policy.expected_input_manifest_identity,
            "expected_output_manifest_id": policy.expected_output_manifest_id,
            "expected_output_manifest_identity": policy.expected_output_manifest_identity,
            "allowed_input_classifications": sorted(item.value for item in policy.allowed_input_classifications),
            "prohibited_input_classifications": sorted(item.value for item in policy.prohibited_input_classifications),
            "fixture_provenance_contract": _fixture_contract_payload(policy.fixture_provenance_contract),
            "permitted_recipient_actor_roles": sorted(
                [[actor_id, role.value] for actor_id, role in policy.permitted_recipient_actor_roles],
                key=lambda item: (item[0], item[1]),
            ),
        }
    )


def _validate_fixture_contract(contract: FixtureProvenanceContract) -> ValidationResult:
    required_strings = (
        contract.expected_fixture_id,
        contract.expected_generator_identity,
        contract.expected_generator_version,
        contract.expected_fixture_provenance_identity,
    )
    if any(not _resolved_identity(value) for value in required_strings):
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_CONTRACT_REQUIRED_IDENTITY_MISSING_OR_AMBIGUOUS")
    if _SHA256_IDENTITY.fullmatch(contract.expected_fixture_provenance_identity) is None:
        return _invalid(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_CONTRACT_EXPECTED_IDENTITY_NOT_SHA256")
    if not contract.expected_construction_input_classes:
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "FIXTURE_CONTRACT_CONSTRUCTION_CLASSES_EMPTY")
    if len(set(contract.expected_construction_input_classes)) != len(contract.expected_construction_input_classes):
        return _invalid(StopReason.PROHIBITED_INPUT_CLASS, "FIXTURE_CONTRACT_DUPLICATE_CONSTRUCTION_CLASS")
    if any(
        item in (InputClassification.UNKNOWN, InputClassification.PROHIBITED)
        for item in contract.expected_construction_input_classes
    ):
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "FIXTURE_CONTRACT_PROHIBITED_CONSTRUCTION_CLASS")
    if not contract.expected_lineage_references:
        return _blocked(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_CONTRACT_LINEAGE_EMPTY")
    if len(set(contract.expected_lineage_references)) != len(contract.expected_lineage_references):
        return _invalid(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_CONTRACT_DUPLICATE_LINEAGE")
    if any(not _resolved_identity(value) for value in contract.expected_lineage_references):
        return _blocked(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_CONTRACT_LINEAGE_AMBIGUOUS")
    if not contract.required_reproducibility_keys:
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_CONTRACT_REQUIRED_REPRO_KEYS_EMPTY")
    if not contract.allowed_reproducibility_keys:
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_CONTRACT_ALLOWED_REPRO_KEYS_EMPTY")
    if len(set(contract.required_reproducibility_keys)) != len(contract.required_reproducibility_keys):
        return _invalid(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_CONTRACT_DUPLICATE_REQUIRED_REPRO_KEY")
    if len(set(contract.allowed_reproducibility_keys)) != len(contract.allowed_reproducibility_keys):
        return _invalid(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_CONTRACT_DUPLICATE_ALLOWED_REPRO_KEY")
    if any(not _resolved_identity(value) for value in contract.required_reproducibility_keys):
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_CONTRACT_REQUIRED_REPRO_KEY_AMBIGUOUS")
    if any(not _resolved_identity(value) for value in contract.allowed_reproducibility_keys):
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_CONTRACT_ALLOWED_REPRO_KEY_AMBIGUOUS")
    if not set(contract.required_reproducibility_keys).issubset(contract.allowed_reproducibility_keys):
        return _invalid(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_CONTRACT_REQUIRED_REPRO_KEYS_NOT_ALLOWED")
    return _valid("FIXTURE_PROVENANCE_CONTRACT_VALID")


def validate_policy(policy: HarnessPolicy) -> ValidationResult:
    required_strings = (
        policy.expected_owner_authority_sha,
        policy.expected_harness_identity,
        policy.expected_harness_version_or_commit_identity,
        policy.expected_manifest_version_identity,
        policy.expected_input_manifest_id,
        policy.expected_input_manifest_identity,
        policy.expected_output_manifest_id,
        policy.expected_output_manifest_identity,
    )
    if any(not _resolved_identity(value) for value in required_strings):
        return _blocked(StopReason.MISSING_AUTHORITY, "POLICY_REQUIRED_IDENTITY_MISSING_OR_AMBIGUOUS")
    if _SHA40.fullmatch(policy.expected_owner_authority_sha) is None:
        return _invalid(StopReason.MISSING_AUTHORITY, "POLICY_OWNER_SHA_NOT_EXACT_40_HEX")
    if _SHA256_IDENTITY.fullmatch(policy.expected_input_manifest_identity) is None:
        return _invalid(StopReason.INPUT_MANIFEST_MISMATCH, "POLICY_EXPECTED_INPUT_MANIFEST_IDENTITY_NOT_SHA256")
    if _SHA256_IDENTITY.fullmatch(policy.expected_output_manifest_identity) is None:
        return _invalid(StopReason.OUTPUT_MANIFEST_MISMATCH, "POLICY_EXPECTED_OUTPUT_MANIFEST_IDENTITY_NOT_SHA256")
    if not policy.allowed_input_classifications or not policy.prohibited_input_classifications:
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "POLICY_INPUT_CLASS_SET_EMPTY")
    if set(policy.allowed_input_classifications).intersection(policy.prohibited_input_classifications):
        return _invalid(StopReason.PROHIBITED_INPUT_CLASS, "POLICY_INPUT_CLASS_OVERLAP")
    if InputClassification.UNKNOWN not in policy.prohibited_input_classifications:
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "POLICY_UNKNOWN_CLASS_NOT_PROHIBITED")
    if InputClassification.PROHIBITED not in policy.prohibited_input_classifications:
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "POLICY_PROHIBITED_CLASS_NOT_PROHIBITED")

    actor_ids = tuple(actor_id for actor_id, _ in policy.permitted_recipient_actor_roles)
    if len(set(actor_ids)) != len(actor_ids):
        return _invalid(StopReason.UNAUTHORIZED_RECIPIENT, "POLICY_DUPLICATE_RECIPIENT_ACTOR_ID")
    if any(not _resolved_identity(actor_id) for actor_id in actor_ids):
        return _blocked(StopReason.UNAUTHORIZED_RECIPIENT, "POLICY_RECIPIENT_ACTOR_ID_AMBIGUOUS")

    if policy.fixture_provenance_contract is not None:
        fixture_contract_result = _validate_fixture_contract(policy.fixture_provenance_contract)
        if fixture_contract_result.state is not ValidationState.VALID:
            return fixture_contract_result
    return _valid("POLICY_STRUCTURALLY_VALID")


def _resolve_trusted_root(
    binding: AuthorityBinding,
    policy: HarnessPolicy,
) -> tuple[ValidationResult, TrustedExecutionPolicyRoot | None]:
    root = get_trusted_execution_policy_root()
    if root is None:
        return _blocked(
            StopReason.MISSING_EXECUTION_POLICY_ROOT,
            "NO_TRUSTED_EXECUTION_POLICY_ROOT_DENY_ALL",
        ), None

    root_strings = (
        root.execution_policy_authority_sha,
        root.expected_construction_authority_sha,
        root.expected_harness_identity,
        root.expected_harness_version_or_commit_identity,
        root.expected_policy_identity,
    )
    if any(not _resolved_identity(value) for value in root_strings):
        return _blocked(StopReason.EXECUTION_POLICY_ROOT_MISMATCH, "TRUSTED_ROOT_REQUIRED_FIELD_MISSING_OR_AMBIGUOUS"), None
    if _SHA40.fullmatch(root.execution_policy_authority_sha) is None:
        return _invalid(StopReason.EXECUTION_POLICY_ROOT_MISMATCH, "EXECUTION_POLICY_AUTHORITY_SHA_NOT_EXACT_40_HEX"), None
    if _SHA40.fullmatch(root.expected_construction_authority_sha) is None:
        return _invalid(StopReason.EXECUTION_POLICY_ROOT_MISMATCH, "ROOT_CONSTRUCTION_AUTHORITY_SHA_NOT_EXACT_40_HEX"), None
    if _SHA256_IDENTITY.fullmatch(root.expected_policy_identity) is None:
        return _invalid(StopReason.EXECUTION_POLICY_ROOT_MISMATCH, "ROOT_POLICY_IDENTITY_NOT_SHA256"), None

    policy_result = validate_policy(policy)
    if policy_result.state is not ValidationState.VALID:
        return policy_result, None
    if root.expected_policy_identity != harness_policy_identity(policy):
        return _blocked(StopReason.EXECUTION_POLICY_ROOT_MISMATCH, "TRUSTED_ROOT_POLICY_IDENTITY_MISMATCH"), None
    if root.expected_construction_authority_sha != binding.owner_authority_sha:
        return _blocked(StopReason.EXECUTION_POLICY_ROOT_MISMATCH, "TRUSTED_ROOT_CONSTRUCTION_AUTHORITY_MISMATCH"), None
    if root.expected_harness_identity != binding.harness_identity:
        return _blocked(StopReason.EXECUTION_POLICY_ROOT_MISMATCH, "TRUSTED_ROOT_HARNESS_IDENTITY_MISMATCH"), None
    if root.expected_harness_version_or_commit_identity != binding.harness_version_or_commit_identity:
        return _blocked(StopReason.EXECUTION_POLICY_ROOT_MISMATCH, "TRUSTED_ROOT_HARNESS_VERSION_MISMATCH"), None
    return _valid("TRUSTED_EXECUTION_POLICY_ROOT_RESOLVED"), root


def validate_authority(binding: AuthorityBinding, policy: HarnessPolicy) -> ValidationResult:
    root_result, _ = _resolve_trusted_root(binding, policy)
    if root_result.state is not ValidationState.VALID:
        return root_result

    required_strings = (
        binding.owner_authority_sha,
        binding.harness_identity,
        binding.harness_version_or_commit_identity,
        binding.manifest_version_identity,
    )
    if any(not _resolved_identity(value) for value in required_strings):
        return _blocked(StopReason.MISSING_AUTHORITY, "AUTHORITY_BINDING_REQUIRED_FIELD_MISSING_OR_AMBIGUOUS")
    if _SHA40.fullmatch(binding.owner_authority_sha) is None:
        return _invalid(StopReason.MISSING_AUTHORITY, "OWNER_AUTHORITY_SHA_NOT_EXACT_40_HEX")
    if binding.owner_authority_sha != policy.expected_owner_authority_sha:
        return _blocked(StopReason.AUTHORITY_MISMATCH, "OWNER_AUTHORITY_SHA_MISMATCH")
    if binding.harness_identity != policy.expected_harness_identity:
        return _blocked(StopReason.AUTHORITY_MISMATCH, "HARNESS_IDENTITY_MISMATCH")
    if binding.harness_version_or_commit_identity != policy.expected_harness_version_or_commit_identity:
        return _blocked(StopReason.AUTHORITY_MISMATCH, "HARNESS_VERSION_OR_COMMIT_IDENTITY_MISMATCH")
    if binding.manifest_version_identity != policy.expected_manifest_version_identity:
        return _blocked(StopReason.AUTHORITY_MISMATCH, "MANIFEST_VERSION_IDENTITY_MISMATCH")
    return _valid("AUTHORITY_AND_TRUSTED_ROOT_VALID")


def validate_input_manifest(
    manifest: InputManifest,
    binding: AuthorityBinding,
    policy: HarnessPolicy,
) -> ValidationResult:
    if manifest.input_id != policy.expected_input_manifest_id:
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_ID_MISMATCH")
    if manifest.manifest_version_identity != binding.manifest_version_identity:
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_MANIFEST_VERSION_MISMATCH")
    if not _resolved_identity(manifest.source_provenance_class):
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "INPUT_PROVENANCE_CLASS_MISSING_OR_AMBIGUOUS")
    if not manifest.exact_permitted_fields or not manifest.exact_prohibited_fields:
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_FIELD_ALLOW_OR_DENY_LIST_EMPTY")
    if any(not _resolved_identity(value) for value in manifest.exact_permitted_fields):
        return _invalid(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_PERMITTED_FIELD_EMPTY_OR_AMBIGUOUS")
    if any(not _resolved_identity(value) for value in manifest.exact_prohibited_fields):
        return _invalid(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_PROHIBITED_FIELD_EMPTY_OR_AMBIGUOUS")
    if _has_wildcard(manifest.exact_permitted_fields) or _has_wildcard(manifest.exact_prohibited_fields):
        return _invalid(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_WILDCARD_FIELD_RULE_PROHIBITED")
    if set(manifest.exact_permitted_fields).intersection(manifest.exact_prohibited_fields):
        return _invalid(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_FIELD_ALLOW_DENY_OVERLAP")
    if not manifest.permitted_reader_roles:
        return _blocked(StopReason.UNAUTHORIZED_READER, "INPUT_READER_ROLE_SET_EMPTY")
    if manifest.input_classification in policy.prohibited_input_classifications:
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "INPUT_CLASS_EXPLICITLY_PROHIBITED")
    if manifest.input_classification not in policy.allowed_input_classifications:
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "INPUT_CLASS_NOT_EXPLICITLY_ALLOWED")

    visibility_states = (
        manifest.raw_values_visible,
        manifest.timestamps_visible,
        manifest.frequency_or_count_information_visible,
    )
    if any(state is VisibilityState.UNRESOLVED for state in visibility_states):
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_VISIBILITY_UNRESOLVED")
    permission_states = (
        manifest.longitudinal_observation_allowed,
        manifest.aggregation_allowed,
        manifest.cross_source_comparison_allowed,
    )
    if any(state is PermissionState.UNRESOLVED for state in permission_states):
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_PERMISSION_UNRESOLVED")
    if manifest.efficacy_leakage_assessment is not LeakageAssessment.CLEAR:
        return _blocked(StopReason.UNEXPECTED_EFFICACY_LEAKAGE, "INPUT_EFFICACY_LEAKAGE_NOT_CLEAR")
    if manifest.access_logging_requirement is not RequirementState.REQUIRED:
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_ACCESS_LOGGING_NOT_EXPLICITLY_REQUIRED")
    if manifest.quarantine_on_ambiguity is not RequirementState.REQUIRED:
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_QUARANTINE_ON_AMBIGUITY_NOT_REQUIRED")
    if manifest.owner_approval_required is RequirementState.UNRESOLVED:
        return _blocked(StopReason.MISSING_AUTHORITY, "INPUT_OWNER_APPROVAL_REQUIREMENT_UNRESOLVED")
    if input_manifest_identity(manifest) != policy.expected_input_manifest_identity:
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_MANIFEST_STRUCTURAL_IDENTITY_MISMATCH")
    return _valid("INPUT_MANIFEST_VALID")


def validate_output_manifest(
    manifest: OutputManifest,
    binding: AuthorityBinding,
    policy: HarnessPolicy,
) -> ValidationResult:
    if manifest.output_id != policy.expected_output_manifest_id:
        return _blocked(StopReason.OUTPUT_MANIFEST_MISMATCH, "OUTPUT_ID_MISMATCH")
    if manifest.manifest_version_identity != binding.manifest_version_identity:
        return _blocked(StopReason.OUTPUT_MANIFEST_MISMATCH, "OUTPUT_MANIFEST_VERSION_MISMATCH")
    required_strings = (
        manifest.output_type,
        manifest.exact_metric_or_artifact,
        manifest.granularity,
        manifest.retention_rule,
        manifest.incident_if_unexpected_information_revealed,
    )
    if any(not _resolved_identity(value) for value in required_strings):
        return _blocked(StopReason.OUTPUT_MANIFEST_MISMATCH, "OUTPUT_REQUIRED_FIELD_MISSING_OR_AMBIGUOUS")
    if any("*" in value for value in required_strings):
        return _invalid(StopReason.OUTPUT_MANIFEST_MISMATCH, "OUTPUT_WILDCARD_RULE_PROHIBITED")
    if not manifest.permitted_recipients:
        return _blocked(StopReason.UNAUTHORIZED_RECIPIENT, "OUTPUT_RECIPIENT_ROLE_SET_EMPTY")
    if manifest.exportability is PermissionState.UNRESOLVED:
        return _blocked(StopReason.OUTPUT_MANIFEST_MISMATCH, "OUTPUT_EXPORTABILITY_UNRESOLVED")
    if manifest.release_approval_requirement is RequirementState.UNRESOLVED:
        return _blocked(StopReason.RELEASE_NOT_AUTHORIZED, "OUTPUT_RELEASE_REQUIREMENT_UNRESOLVED")
    if output_manifest_identity(manifest) != policy.expected_output_manifest_identity:
        return _blocked(StopReason.OUTPUT_MANIFEST_MISMATCH, "OUTPUT_MANIFEST_STRUCTURAL_IDENTITY_MISMATCH")
    return _valid("OUTPUT_MANIFEST_VALID")


def validate_fixture_provenance(
    provenance: FixtureProvenance,
    policy: HarnessPolicy,
) -> ValidationResult:
    contract = policy.fixture_provenance_contract
    if contract is None:
        return _blocked(
            StopReason.FIXTURE_PROVENANCE_MISMATCH,
            "NO_APPROVED_FIXTURE_PROVENANCE_CONTRACT",
        )
    contract_result = _validate_fixture_contract(contract)
    if contract_result.state is not ValidationState.VALID:
        return contract_result

    required_strings = (
        provenance.fixture_id,
        provenance.generator_identity,
        provenance.generator_version,
    )
    if any(not _resolved_identity(value) for value in required_strings):
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "FIXTURE_PROVENANCE_IDENTITY_MISSING_OR_AMBIGUOUS")
    if provenance.fixture_id != contract.expected_fixture_id:
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_ID_MISMATCH")
    if provenance.generator_identity != contract.expected_generator_identity:
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_GENERATOR_IDENTITY_MISMATCH")
    if provenance.generator_version != contract.expected_generator_version:
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_GENERATOR_VERSION_MISMATCH")

    if not provenance.construction_input_classes:
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "FIXTURE_CONSTRUCTION_INPUT_CLASSES_EMPTY")
    if len(set(provenance.construction_input_classes)) != len(provenance.construction_input_classes):
        return _invalid(StopReason.PROHIBITED_INPUT_CLASS, "FIXTURE_DUPLICATE_CONSTRUCTION_CLASS")
    if any(item in (InputClassification.UNKNOWN, InputClassification.PROHIBITED) for item in provenance.construction_input_classes):
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "FIXTURE_CONSTRUCTION_INPUT_CLASS_PROHIBITED")
    if sorted(item.value for item in provenance.construction_input_classes) != sorted(
        item.value for item in contract.expected_construction_input_classes
    ):
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_CONSTRUCTION_INPUT_CLASSES_MISMATCH")

    if not provenance.lineage_references:
        return _blocked(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_LINEAGE_REFERENCES_EMPTY")
    if len(set(provenance.lineage_references)) != len(provenance.lineage_references):
        return _invalid(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_DUPLICATE_LINEAGE_REFERENCE")
    if any(not _resolved_identity(value) for value in provenance.lineage_references):
        return _blocked(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_LINEAGE_REFERENCE_EMPTY_OR_AMBIGUOUS")
    if sorted(provenance.lineage_references) != sorted(contract.expected_lineage_references):
        return _blocked(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_LINEAGE_REFERENCE_SET_MISMATCH")

    if not provenance.reproducibility_metadata:
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "FIXTURE_REPRODUCIBILITY_METADATA_EMPTY")
    metadata_keys = tuple(key for key, _ in provenance.reproducibility_metadata)
    if len(set(metadata_keys)) != len(metadata_keys):
        return _invalid(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_DUPLICATE_REPRODUCIBILITY_KEY")
    if any(
        not _resolved_identity(key) or not _resolved_identity(value)
        for key, value in provenance.reproducibility_metadata
    ):
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "FIXTURE_REPRODUCIBILITY_METADATA_INCOMPLETE_OR_AMBIGUOUS")
    if not set(contract.required_reproducibility_keys).issubset(metadata_keys):
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_REQUIRED_REPRODUCIBILITY_KEY_MISSING")
    if not set(metadata_keys).issubset(contract.allowed_reproducibility_keys):
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_UNEXPECTED_REPRODUCIBILITY_KEY")

    if provenance.contamination_state is ContaminationState.UNKNOWN:
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "FIXTURE_CONTAMINATION_STATE_UNKNOWN")
    if provenance.contamination_state is ContaminationState.CONTAMINATED:
        return _blocked(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_CONTAMINATED")
    if provenance.admissibility_state is not AdmissibilityState.ADMISSIBLE:
        return _blocked(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_ADMISSIBILITY_NOT_EXPLICIT")
    if fixture_provenance_identity(provenance) != contract.expected_fixture_provenance_identity:
        return _blocked(StopReason.FIXTURE_PROVENANCE_MISMATCH, "FIXTURE_PROVENANCE_STRUCTURAL_IDENTITY_MISMATCH")
    return _valid("FIXTURE_PROVENANCE_VALID")


def validate_role_authorization(
    declaration: RoleDeclaration,
    authorization: ActionAuthorization,
    required_action: Action,
    trusted_root: TrustedExecutionPolicyRoot,
    unauthorized_reason: StopReason,
) -> ValidationResult:
    if not _resolved_identity(declaration.actor_id):
        return _blocked(unauthorized_reason, "DECLARED_ACTOR_ID_MISSING_OR_AMBIGUOUS")
    if not _resolved_identity(authorization.authorization_id):
        return _blocked(unauthorized_reason, "ACTION_AUTHORIZATION_ID_MISSING_OR_AMBIGUOUS")
    if not _resolved_identity(authorization.actor_id):
        return _blocked(unauthorized_reason, "ACTION_AUTHORIZATION_ACTOR_ID_MISSING_OR_AMBIGUOUS")
    if declaration.actor_id != authorization.actor_id:
        return _blocked(unauthorized_reason, "ACTION_AUTHORIZATION_ACTOR_MISMATCH")
    if declaration.declared_role is not authorization.declared_role:
        return _blocked(unauthorized_reason, "ACTION_AUTHORIZATION_ROLE_MISMATCH")
    if authorization.action is not required_action:
        return _blocked(unauthorized_reason, "ACTION_AUTHORIZATION_ACTION_MISMATCH")
    if authorization.authority_sha != trusted_root.execution_policy_authority_sha:
        return _blocked(StopReason.AUTHORITY_MISMATCH, "ACTION_AUTHORIZATION_EXECUTION_POLICY_AUTHORITY_MISMATCH")
    if authorization.state is not AuthorizationState.AUTHORIZED:
        return _blocked(unauthorized_reason, "ACTION_AUTHORIZATION_NOT_AUTHORIZED")
    return _valid("ROLE_ACTION_EXECUTION_AUTHORITY_VALID")


def _validate_exact_recipient(policy: HarnessPolicy, recipient: RoleDeclaration) -> ValidationResult:
    if not _resolved_identity(recipient.actor_id):
        return _blocked(StopReason.UNAUTHORIZED_RECIPIENT, "RECIPIENT_ACTOR_ID_MISSING_OR_AMBIGUOUS")
    if (recipient.actor_id, recipient.declared_role) not in policy.permitted_recipient_actor_roles:
        return _blocked(StopReason.UNAUTHORIZED_RECIPIENT, "RECIPIENT_ACTOR_ROLE_NOT_EXACTLY_AUTHORIZED")
    return _valid("EXACT_RECIPIENT_ACTOR_ROLE_AUTHORIZED")


@dataclass(frozen=True, slots=True)
class A2Harness:
    authority: AuthorityBinding
    policy: HarnessPolicy

    def validate_binding(self) -> ValidationResult:
        return validate_authority(self.authority, self.policy)

    def _trusted_root(self) -> tuple[ValidationResult, TrustedExecutionPolicyRoot | None]:
        return _resolve_trusted_root(self.authority, self.policy)

    def _assess_input_read(
        self,
        manifest: InputManifest,
        declaration: RoleDeclaration,
        authorization: ActionAuthorization,
    ) -> tuple[_ActionAssessment, TrustedExecutionPolicyRoot | None]:
        authority_result, root = self._trusted_root()
        if authority_result.state is not ValidationState.VALID or root is None:
            return _assessment_deny(
                authority_result.stop_reason or StopReason.MISSING_EXECUTION_POLICY_ROOT,
                authority_result.detail_code,
            ), None

        binding_result = validate_authority(self.authority, self.policy)
        if binding_result.state is not ValidationState.VALID:
            return _assessment_deny(
                binding_result.stop_reason or StopReason.MISSING_AUTHORITY,
                binding_result.detail_code,
            ), root
        manifest_result = validate_input_manifest(manifest, self.authority, self.policy)
        if manifest_result.state is not ValidationState.VALID:
            quarantine = (
                QuarantineState.QUARANTINED
                if manifest_result.stop_reason is StopReason.UNEXPECTED_EFFICACY_LEAKAGE
                else QuarantineState.BLOCKED_PENDING_OWNER_REVIEW
            )
            return _assessment_deny(
                manifest_result.stop_reason or StopReason.INPUT_MANIFEST_MISMATCH,
                manifest_result.detail_code,
                quarantine,
            ), root
        if declaration.declared_role not in manifest.permitted_reader_roles:
            return _assessment_deny(
                StopReason.UNAUTHORIZED_READER,
                "DECLARED_ROLE_NOT_IN_INPUT_READER_ALLOWLIST",
            ), root
        authorization_result = validate_role_authorization(
            declaration,
            authorization,
            Action.READ_INPUT,
            root,
            StopReason.UNAUTHORIZED_READER,
        )
        if authorization_result.state is not ValidationState.VALID:
            return _assessment_deny(
                authorization_result.stop_reason or StopReason.UNAUTHORIZED_READER,
                authorization_result.detail_code,
            ), root
        return _assessment_allow("INPUT_READ_ELIGIBLE_PENDING_REQUIRED_LOG", False), root

    def _assess_fixture_metadata_admission(
        self,
        provenance: FixtureProvenance,
        declaration: RoleDeclaration,
        authorization: ActionAuthorization,
    ) -> tuple[_ActionAssessment, TrustedExecutionPolicyRoot | None]:
        authority_result, root = self._trusted_root()
        if authority_result.state is not ValidationState.VALID or root is None:
            return _assessment_deny(
                authority_result.stop_reason or StopReason.MISSING_EXECUTION_POLICY_ROOT,
                authority_result.detail_code,
            ), None
        binding_result = validate_authority(self.authority, self.policy)
        if binding_result.state is not ValidationState.VALID:
            return _assessment_deny(
                binding_result.stop_reason or StopReason.MISSING_AUTHORITY,
                binding_result.detail_code,
            ), root
        provenance_result = validate_fixture_provenance(provenance, self.policy)
        if provenance_result.state is not ValidationState.VALID:
            quarantine = (
                QuarantineState.QUARANTINED
                if provenance_result.stop_reason
                in (
                    StopReason.UNKNOWN_PROVENANCE,
                    StopReason.FIXTURE_LINEAGE_AMBIGUITY,
                    StopReason.FIXTURE_PROVENANCE_MISMATCH,
                )
                else QuarantineState.BLOCKED_PENDING_OWNER_REVIEW
            )
            return _assessment_deny(
                provenance_result.stop_reason or StopReason.UNKNOWN_PROVENANCE,
                provenance_result.detail_code,
                quarantine,
            ), root
        authorization_result = validate_role_authorization(
            declaration,
            authorization,
            Action.ADMIT_FIXTURE_METADATA,
            root,
            StopReason.UNAUTHORIZED_READER,
        )
        if authorization_result.state is not ValidationState.VALID:
            return _assessment_deny(
                authorization_result.stop_reason or StopReason.UNAUTHORIZED_READER,
                authorization_result.detail_code,
            ), root
        return _assessment_allow("FIXTURE_METADATA_ADMISSION_ELIGIBLE_PENDING_REQUIRED_LOG", False), root

    def _assess_output_release(
        self,
        manifest: OutputManifest,
        recipient: RoleDeclaration,
        release_actor: RoleDeclaration,
        release_authorization: ActionAuthorization,
        disclosure_ledger: CumulativeDisclosureLedger,
    ) -> tuple[_ActionAssessment, TrustedExecutionPolicyRoot | None]:
        authority_result, root = self._trusted_root()
        if authority_result.state is not ValidationState.VALID or root is None:
            return _assessment_deny(
                authority_result.stop_reason or StopReason.MISSING_EXECUTION_POLICY_ROOT,
                authority_result.detail_code,
            ), None
        binding_result = validate_authority(self.authority, self.policy)
        if binding_result.state is not ValidationState.VALID:
            return _assessment_deny(
                binding_result.stop_reason or StopReason.MISSING_AUTHORITY,
                binding_result.detail_code,
            ), root
        manifest_result = validate_output_manifest(manifest, self.authority, self.policy)
        if manifest_result.state is not ValidationState.VALID:
            return _assessment_deny(
                manifest_result.stop_reason or StopReason.OUTPUT_MANIFEST_MISMATCH,
                manifest_result.detail_code,
            ), root

        if recipient.declared_role not in manifest.permitted_recipients:
            return _assessment_deny(
                StopReason.UNAUTHORIZED_RECIPIENT,
                "RECIPIENT_ROLE_NOT_IN_OUTPUT_MANIFEST_ALLOWLIST",
            ), root
        recipient_result = _validate_exact_recipient(self.policy, recipient)
        if recipient_result.state is not ValidationState.VALID:
            return _assessment_deny(
                recipient_result.stop_reason or StopReason.UNAUTHORIZED_RECIPIENT,
                recipient_result.detail_code,
            ), root

        if manifest.release_approval_requirement is RequirementState.REQUIRED:
            if not _resolved_identity(release_actor.actor_id):
                return _assessment_deny(
                    StopReason.RELEASE_NOT_AUTHORIZED,
                    "RELEASE_ACTOR_ID_MISSING_OR_AMBIGUOUS",
                ), root
            if release_actor.actor_id == recipient.actor_id:
                return _assessment_deny(
                    StopReason.RELEASE_INDEPENDENCE_VIOLATION,
                    "RELEASE_ACTOR_ID_MUST_DIFFER_FROM_RECIPIENT_ACTOR_ID",
                ), root
            if release_actor.declared_role is not Role.RELEASE_APPROVER:
                return _assessment_deny(
                    StopReason.RELEASE_NOT_AUTHORIZED,
                    "REQUIRED_RELEASE_APPROVER_ROLE_MISSING",
                ), root

        authorization_result = validate_role_authorization(
            release_actor,
            release_authorization,
            Action.RELEASE_OUTPUT,
            root,
            StopReason.RELEASE_NOT_AUTHORIZED,
        )
        if authorization_result.state is not ValidationState.VALID:
            return _assessment_deny(
                authorization_result.stop_reason or StopReason.RELEASE_NOT_AUTHORIZED,
                authorization_result.detail_code,
            ), root
        if manifest.exportability is not PermissionState.ALLOWED:
            return _assessment_deny(StopReason.RELEASE_NOT_AUTHORIZED, "OUTPUT_EXPORTABILITY_NOT_ALLOWED"), root
        if manifest.quarantine_status is not QuarantineState.CLEAR:
            return _assessment_deny(
                StopReason.RELEASE_NOT_AUTHORIZED,
                "OUTPUT_QUARANTINE_STATE_BLOCKS_RELEASE",
                manifest.quarantine_status,
            ), root
        if manifest.efficacy_leakage_assessment is not LeakageAssessment.CLEAR:
            return _assessment_deny(
                StopReason.UNEXPECTED_EFFICACY_LEAKAGE,
                "OUTPUT_EFFICACY_LEAKAGE_NOT_CLEAR",
                QuarantineState.QUARANTINED,
            ), root
        if manifest.cumulative_disclosure_risk is not CumulativeDisclosureState.CLEAR:
            return _assessment_deny(
                StopReason.CUMULATIVE_DISCLOSURE_AMBIGUITY,
                "OUTPUT_MANIFEST_CUMULATIVE_DISCLOSURE_NOT_CLEAR",
                cumulative_disclosure_state=manifest.cumulative_disclosure_risk,
            ), root

        cumulative_state = disclosure_ledger.evaluate_for(
            manifest.output_id,
            recipient.actor_id,
            recipient.declared_role,
        )
        if cumulative_state is not CumulativeDisclosureState.CLEAR:
            return _assessment_deny(
                StopReason.CUMULATIVE_DISCLOSURE_AMBIGUITY,
                "DISCLOSURE_LEDGER_NOT_CLEAR_FOR_EXACT_OUTPUT_RECIPIENT_ACTOR_ROLE",
                cumulative_disclosure_state=cumulative_state,
            ), root
        if manifest.release_approval_requirement not in (
            RequirementState.REQUIRED,
            RequirementState.NOT_REQUIRED,
        ):
            return _assessment_deny(
                StopReason.RELEASE_NOT_AUTHORIZED,
                "RELEASE_APPROVAL_REQUIREMENT_NOT_RESOLVED",
                cumulative_disclosure_state=cumulative_state,
            ), root
        return _assessment_allow(
            "OUTPUT_RELEASE_ELIGIBLE_PENDING_REQUIRED_LOG",
            True,
            cumulative_disclosure_state=cumulative_state,
        ), root

    def _complete_with_required_log(
        self,
        log: StructuredAuditLog,
        log_record_id: str,
        assessment: _ActionAssessment,
        trusted_root: TrustedExecutionPolicyRoot | None,
        actor: RoleDeclaration,
        authorization: ActionAuthorization,
        attempted_action: Action,
        target_kind: TargetKind,
        target_id: str,
        manifest_identity: str,
        incident_identifier: str | None,
        recipient: RoleDeclaration | None,
    ) -> LoggedActionResult:
        if not _resolved_identity(log_record_id):
            return LoggedActionResult(
                _logging_failure("REQUIRED_LOG_RECORD_ID_MISSING_OR_AMBIGUOUS"),
                log,
                None,
                False,
            )
        if any(record.record_id == log_record_id for record in log.records):
            return LoggedActionResult(
                _logging_failure("REQUIRED_LOG_RECORD_ID_ALREADY_EXISTS"),
                log,
                None,
                False,
            )

        predicted_permit = PermitState.PERMIT if assessment.allowed else PermitState.DENY
        predicted_release = (
            ReleaseState.AUTHORIZED
            if assessment.allowed and assessment.release_authorized
            else ReleaseState.BLOCKED
        )
        execution_policy_authority_identity = (
            trusted_root.execution_policy_authority_sha if trusted_root is not None else None
        )
        record = LogRecord(
            record_id=log_record_id,
            construction_authority_identity=self.authority.owner_authority_sha,
            execution_policy_authority_identity=execution_policy_authority_identity,
            authorization_authority_identity=authorization.authority_sha,
            manifest_identity=manifest_identity,
            actor_id=actor.actor_id,
            actor_role=actor.declared_role,
            authorization_id=authorization.authorization_id,
            attempted_action=attempted_action,
            target_kind=target_kind,
            target_id=target_id,
            permit_or_deny_state=predicted_permit,
            quarantine_state=assessment.quarantine_state,
            release_state=predicted_release,
            incident_identifier=incident_identifier,
            cumulative_disclosure_state=assessment.cumulative_disclosure_state,
            recipient_actor_id=recipient.actor_id if recipient is not None else None,
            recipient_role=recipient.declared_role if recipient is not None else None,
        )
        acknowledgement = log.append(record)
        if not acknowledgement.appended or acknowledgement.record_id != log_record_id:
            return LoggedActionResult(
                _logging_failure("REQUIRED_LOG_APPEND_NOT_ACKNOWLEDGED"),
                log,
                None,
                False,
            )

        final_result = _finalize_logged_action_result(
            acknowledgement=acknowledgement,
            log_record=record,
            validation_state=(ValidationState.VALID if assessment.allowed else ValidationState.BLOCKED),
            permit_or_deny_state=predicted_permit,
            quarantine_state=assessment.quarantine_state,
            release_state=predicted_release,
            completion_state=CompletionState.COMPLETED,
            stop_reason=assessment.stop_reason,
            detail_code=assessment.detail_code.replace("PENDING_REQUIRED_LOG", "LOGGED_AND_COMPLETED"),
            expected_construction_authority_identity=self.authority.owner_authority_sha,
            expected_execution_policy_authority_identity=execution_policy_authority_identity,
            expected_actor=actor,
            expected_authorization=authorization,
            expected_action=attempted_action,
            expected_target_kind=target_kind,
            expected_target_id=target_id,
            expected_manifest_identity=manifest_identity,
            expected_incident_identifier=incident_identifier,
            expected_cumulative_disclosure_state=assessment.cumulative_disclosure_state,
            expected_recipient=recipient,
        )
        if final_result is None:
            return LoggedActionResult(
                _logging_failure("FINAL_STATE_LOG_LINKAGE_INVARIANT_FAILED"),
                acknowledgement.log,
                None,
                False,
            )
        return final_result

    def evaluate_input_read(
        self,
        log: StructuredAuditLog,
        log_record_id: str,
        manifest: InputManifest,
        declaration: RoleDeclaration,
        authorization: ActionAuthorization,
        incident_identifier: str | None = None,
    ) -> LoggedActionResult:
        assessment, root = self._assess_input_read(manifest, declaration, authorization)
        return self._complete_with_required_log(
            log,
            log_record_id,
            assessment,
            root,
            declaration,
            authorization,
            Action.READ_INPUT,
            TargetKind.INPUT_MANIFEST,
            manifest.input_id,
            input_manifest_identity(manifest),
            incident_identifier,
            None,
        )

    def evaluate_fixture_metadata_admission(
        self,
        log: StructuredAuditLog,
        log_record_id: str,
        provenance: FixtureProvenance,
        declaration: RoleDeclaration,
        authorization: ActionAuthorization,
        incident_identifier: str | None = None,
    ) -> LoggedActionResult:
        assessment, root = self._assess_fixture_metadata_admission(
            provenance,
            declaration,
            authorization,
        )
        return self._complete_with_required_log(
            log,
            log_record_id,
            assessment,
            root,
            declaration,
            authorization,
            Action.ADMIT_FIXTURE_METADATA,
            TargetKind.FIXTURE_PROVENANCE,
            provenance.fixture_id,
            fixture_provenance_identity(provenance),
            incident_identifier,
            None,
        )

    def evaluate_output_release(
        self,
        log: StructuredAuditLog,
        log_record_id: str,
        manifest: OutputManifest,
        recipient: RoleDeclaration,
        release_actor: RoleDeclaration,
        release_authorization: ActionAuthorization,
        disclosure_ledger: CumulativeDisclosureLedger,
        incident_identifier: str | None = None,
    ) -> LoggedActionResult:
        assessment, root = self._assess_output_release(
            manifest,
            recipient,
            release_actor,
            release_authorization,
            disclosure_ledger,
        )
        return self._complete_with_required_log(
            log,
            log_record_id,
            assessment,
            root,
            release_actor,
            release_authorization,
            Action.RELEASE_OUTPUT,
            TargetKind.OUTPUT_MANIFEST,
            manifest.output_id,
            output_manifest_identity(manifest),
            incident_identifier,
            recipient,
        )

    def validate_resource_boundary(self, state: ResourceBoundaryState) -> ValidationResult:
        authority_result = self.validate_binding()
        if authority_result.state is not ValidationState.VALID:
            return authority_result
        if state is not ResourceBoundaryState.WITHIN_AUTHORITY:
            return _blocked(
                StopReason.RESOURCE_BOUNDARY_UNRESOLVED,
                "RESOURCE_BOUNDARY_NOT_EXPLICITLY_WITHIN_AUTHORITY",
            )
        return _valid("RESOURCE_BOUNDARY_WITHIN_AUTHORITY")

    def stop_for_unexpected_efficacy_leakage(self) -> ValidationResult:
        return _blocked(
            StopReason.UNEXPECTED_EFFICACY_LEAKAGE,
            "UNEXPECTED_EFFICACY_LEAKAGE_FAIL_CLOSED_STOP",
        )
