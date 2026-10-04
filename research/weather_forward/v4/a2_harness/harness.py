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
    ContaminationState,
    CumulativeDisclosureLedger,
    CumulativeDisclosureState,
    FixtureProvenance,
    HarnessDecision,
    InputClassification,
    InputManifest,
    LeakageAssessment,
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
    ValidationResult,
    ValidationState,
    VisibilityState,
)


_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256_IDENTITY = re.compile(r"^sha256:[0-9a-f]{64}$")
_AMBIGUOUS_TOKENS = frozenset({"UNKNOWN", "UNRESOLVED", "AMBIGUOUS", "NOT_ATTESTED"})


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


def _blocked(reason: StopReason, detail_code: str) -> ValidationResult:
    return ValidationResult(
        state=ValidationState.BLOCKED,
        stop_reason=reason,
        detail_code=detail_code,
    )


def _invalid(reason: StopReason, detail_code: str) -> ValidationResult:
    return ValidationResult(
        state=ValidationState.INVALID,
        stop_reason=reason,
        detail_code=detail_code,
    )


def _valid(detail_code: str) -> ValidationResult:
    return ValidationResult(
        state=ValidationState.VALID,
        stop_reason=None,
        detail_code=detail_code,
    )


def _deny(
    reason: StopReason,
    detail_code: str,
    quarantine_state: QuarantineState = QuarantineState.BLOCKED_PENDING_OWNER_REVIEW,
) -> HarnessDecision:
    return HarnessDecision(
        validation_state=ValidationState.BLOCKED,
        permit_or_deny_state=PermitState.DENY,
        quarantine_state=quarantine_state,
        release_state=ReleaseState.BLOCKED,
        stop_reason=reason,
        detail_code=detail_code,
    )


def _permit(detail_code: str, release_state: ReleaseState) -> HarnessDecision:
    return HarnessDecision(
        validation_state=ValidationState.VALID,
        permit_or_deny_state=PermitState.PERMIT,
        quarantine_state=QuarantineState.CLEAR,
        release_state=release_state,
        stop_reason=None,
        detail_code=detail_code,
    )


def _nonempty(value: str) -> bool:
    return bool(value and value.strip())


def _ambiguous(value: str) -> bool:
    return value.strip().upper() in _AMBIGUOUS_TOKENS


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
    """Return a deterministic identity covering every material input-manifest field."""
    return _canonical_digest(
        {
            "manifest_kind": "InputManifest",
            "input_id": manifest.input_id,
            "manifest_version_identity": manifest.manifest_version_identity,
            "input_classification": manifest.input_classification.value,
            "source_provenance_class": manifest.source_provenance_class,
            "exact_permitted_fields": sorted(manifest.exact_permitted_fields),
            "exact_prohibited_fields": sorted(manifest.exact_prohibited_fields),
            "permitted_reader_roles": sorted(
                role.value for role in manifest.permitted_reader_roles
            ),
            "raw_values_visible": manifest.raw_values_visible.value,
            "timestamps_visible": manifest.timestamps_visible.value,
            "frequency_or_count_information_visible": (
                manifest.frequency_or_count_information_visible.value
            ),
            "longitudinal_observation_allowed": (
                manifest.longitudinal_observation_allowed.value
            ),
            "aggregation_allowed": manifest.aggregation_allowed.value,
            "cross_source_comparison_allowed": (
                manifest.cross_source_comparison_allowed.value
            ),
            "efficacy_leakage_assessment": manifest.efficacy_leakage_assessment.value,
            "access_logging_requirement": manifest.access_logging_requirement.value,
            "quarantine_on_ambiguity": manifest.quarantine_on_ambiguity.value,
            "owner_approval_required": manifest.owner_approval_required.value,
        }
    )


def output_manifest_identity(manifest: OutputManifest) -> str:
    """Return a deterministic identity covering every material output-manifest field."""
    return _canonical_digest(
        {
            "manifest_kind": "OutputManifest",
            "output_id": manifest.output_id,
            "manifest_version_identity": manifest.manifest_version_identity,
            "output_type": manifest.output_type,
            "exact_metric_or_artifact": manifest.exact_metric_or_artifact,
            "granularity": manifest.granularity,
            "permitted_recipients": sorted(
                role.value for role in manifest.permitted_recipients
            ),
            "exportability": manifest.exportability.value,
            "quarantine_status": manifest.quarantine_status.value,
            "cumulative_disclosure_risk": manifest.cumulative_disclosure_risk.value,
            "efficacy_leakage_assessment": manifest.efficacy_leakage_assessment.value,
            "release_approval_requirement": (
                manifest.release_approval_requirement.value
            ),
            "retention_rule": manifest.retention_rule,
            "incident_if_unexpected_information_revealed": (
                manifest.incident_if_unexpected_information_revealed
            ),
        }
    )


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
    if any(not _nonempty(value) for value in required_strings):
        return _blocked(StopReason.MISSING_AUTHORITY, "POLICY_REQUIRED_IDENTITY_MISSING")
    if any(_ambiguous(value) for value in required_strings):
        return _blocked(StopReason.MISSING_AUTHORITY, "POLICY_REQUIRED_IDENTITY_AMBIGUOUS")
    if _SHA40.fullmatch(policy.expected_owner_authority_sha) is None:
        return _invalid(StopReason.MISSING_AUTHORITY, "POLICY_OWNER_SHA_NOT_EXACT_40_HEX")
    if _SHA256_IDENTITY.fullmatch(policy.expected_input_manifest_identity) is None:
        return _invalid(
            StopReason.INPUT_MANIFEST_MISMATCH,
            "POLICY_EXPECTED_INPUT_MANIFEST_IDENTITY_NOT_SHA256",
        )
    if _SHA256_IDENTITY.fullmatch(policy.expected_output_manifest_identity) is None:
        return _invalid(
            StopReason.OUTPUT_MANIFEST_MISMATCH,
            "POLICY_EXPECTED_OUTPUT_MANIFEST_IDENTITY_NOT_SHA256",
        )
    if not policy.allowed_input_classifications:
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "POLICY_ALLOWED_INPUT_CLASSES_EMPTY")
    if not policy.prohibited_input_classifications:
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "POLICY_PROHIBITED_INPUT_CLASSES_EMPTY")
    if set(policy.allowed_input_classifications).intersection(
        policy.prohibited_input_classifications
    ):
        return _invalid(StopReason.PROHIBITED_INPUT_CLASS, "POLICY_INPUT_CLASS_OVERLAP")
    if InputClassification.UNKNOWN not in policy.prohibited_input_classifications:
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "POLICY_UNKNOWN_CLASS_NOT_PROHIBITED")
    if InputClassification.PROHIBITED not in policy.prohibited_input_classifications:
        return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "POLICY_PROHIBITED_CLASS_NOT_PROHIBITED")
    return _valid("POLICY_VALID")


def validate_authority(
    binding: AuthorityBinding,
    policy: HarnessPolicy,
) -> ValidationResult:
    policy_result = validate_policy(policy)
    if policy_result.state is not ValidationState.VALID:
        return policy_result

    required_strings = (
        binding.owner_authority_sha,
        binding.harness_identity,
        binding.harness_version_or_commit_identity,
        binding.manifest_version_identity,
    )
    if any(not _nonempty(value) for value in required_strings):
        return _blocked(StopReason.MISSING_AUTHORITY, "AUTHORITY_BINDING_REQUIRED_FIELD_MISSING")
    if any(_ambiguous(value) for value in required_strings):
        return _blocked(StopReason.MISSING_AUTHORITY, "AUTHORITY_BINDING_REQUIRED_FIELD_AMBIGUOUS")
    if _SHA40.fullmatch(binding.owner_authority_sha) is None:
        return _invalid(StopReason.MISSING_AUTHORITY, "OWNER_AUTHORITY_SHA_NOT_EXACT_40_HEX")
    if binding.owner_authority_sha != policy.expected_owner_authority_sha:
        return _blocked(StopReason.AUTHORITY_MISMATCH, "OWNER_AUTHORITY_SHA_MISMATCH")
    if binding.harness_identity != policy.expected_harness_identity:
        return _blocked(StopReason.AUTHORITY_MISMATCH, "HARNESS_IDENTITY_MISMATCH")
    if (
        binding.harness_version_or_commit_identity
        != policy.expected_harness_version_or_commit_identity
    ):
        return _blocked(StopReason.AUTHORITY_MISMATCH, "HARNESS_VERSION_OR_COMMIT_IDENTITY_MISMATCH")
    if binding.manifest_version_identity != policy.expected_manifest_version_identity:
        return _blocked(StopReason.AUTHORITY_MISMATCH, "MANIFEST_VERSION_IDENTITY_MISMATCH")
    return _valid("AUTHORITY_BINDING_VALID")


def validate_input_manifest(
    manifest: InputManifest,
    binding: AuthorityBinding,
    policy: HarnessPolicy,
) -> ValidationResult:
    if manifest.input_id != policy.expected_input_manifest_id:
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_ID_MISMATCH")
    if manifest.manifest_version_identity != binding.manifest_version_identity:
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_MANIFEST_VERSION_MISMATCH")
    if not _nonempty(manifest.source_provenance_class) or _ambiguous(
        manifest.source_provenance_class
    ):
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "INPUT_PROVENANCE_CLASS_MISSING_OR_AMBIGUOUS")
    if not manifest.exact_permitted_fields or not manifest.exact_prohibited_fields:
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_FIELD_ALLOW_OR_DENY_LIST_EMPTY")
    if any(not _nonempty(value) for value in manifest.exact_permitted_fields):
        return _invalid(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_PERMITTED_FIELD_EMPTY")
    if any(not _nonempty(value) for value in manifest.exact_prohibited_fields):
        return _invalid(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_PROHIBITED_FIELD_EMPTY")
    if _has_wildcard(manifest.exact_permitted_fields) or _has_wildcard(
        manifest.exact_prohibited_fields
    ):
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

    if manifest.efficacy_leakage_assessment is LeakageAssessment.BLOCKED:
        return _blocked(StopReason.UNEXPECTED_EFFICACY_LEAKAGE, "INPUT_EFFICACY_LEAKAGE_BLOCKED")
    if manifest.efficacy_leakage_assessment is LeakageAssessment.UNRESOLVED:
        return _blocked(StopReason.UNEXPECTED_EFFICACY_LEAKAGE, "INPUT_EFFICACY_LEAKAGE_UNRESOLVED")
    if manifest.access_logging_requirement is not RequirementState.REQUIRED:
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_ACCESS_LOGGING_NOT_EXPLICITLY_REQUIRED")
    if manifest.quarantine_on_ambiguity is not RequirementState.REQUIRED:
        return _blocked(StopReason.INPUT_MANIFEST_MISMATCH, "INPUT_QUARANTINE_ON_AMBIGUITY_NOT_REQUIRED")
    if manifest.owner_approval_required is RequirementState.UNRESOLVED:
        return _blocked(StopReason.MISSING_AUTHORITY, "INPUT_OWNER_APPROVAL_REQUIREMENT_UNRESOLVED")
    if input_manifest_identity(manifest) != policy.expected_input_manifest_identity:
        return _blocked(
            StopReason.INPUT_MANIFEST_MISMATCH,
            "INPUT_MANIFEST_STRUCTURAL_IDENTITY_MISMATCH",
        )
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
    if any(not _nonempty(value) for value in required_strings):
        return _blocked(StopReason.OUTPUT_MANIFEST_MISMATCH, "OUTPUT_REQUIRED_FIELD_MISSING")
    if any(_ambiguous(value) for value in required_strings):
        return _blocked(StopReason.OUTPUT_MANIFEST_MISMATCH, "OUTPUT_REQUIRED_FIELD_AMBIGUOUS")
    if any("*" in value for value in required_strings):
        return _invalid(StopReason.OUTPUT_MANIFEST_MISMATCH, "OUTPUT_WILDCARD_RULE_PROHIBITED")
    if not manifest.permitted_recipients:
        return _blocked(StopReason.UNAUTHORIZED_RECIPIENT, "OUTPUT_RECIPIENT_ROLE_SET_EMPTY")
    if manifest.exportability is PermissionState.UNRESOLVED:
        return _blocked(StopReason.OUTPUT_MANIFEST_MISMATCH, "OUTPUT_EXPORTABILITY_UNRESOLVED")
    if manifest.release_approval_requirement is RequirementState.UNRESOLVED:
        return _blocked(StopReason.RELEASE_NOT_AUTHORIZED, "OUTPUT_RELEASE_REQUIREMENT_UNRESOLVED")
    if output_manifest_identity(manifest) != policy.expected_output_manifest_identity:
        return _blocked(
            StopReason.OUTPUT_MANIFEST_MISMATCH,
            "OUTPUT_MANIFEST_STRUCTURAL_IDENTITY_MISMATCH",
        )
    return _valid("OUTPUT_MANIFEST_VALID")


def validate_fixture_provenance(
    provenance: FixtureProvenance,
    allowed_construction_input_classes: tuple[InputClassification, ...],
) -> ValidationResult:
    required_strings = (
        provenance.fixture_id,
        provenance.generator_identity,
        provenance.generator_version,
    )
    if any(not _nonempty(value) or _ambiguous(value) for value in required_strings):
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "FIXTURE_PROVENANCE_IDENTITY_MISSING_OR_AMBIGUOUS")
    if not provenance.construction_input_classes:
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "FIXTURE_CONSTRUCTION_INPUT_CLASSES_EMPTY")
    if not provenance.lineage_references:
        return _blocked(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_LINEAGE_REFERENCES_EMPTY")
    if any(
        not _nonempty(value) or _ambiguous(value)
        for value in provenance.lineage_references
    ):
        return _blocked(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_LINEAGE_REFERENCE_EMPTY_OR_AMBIGUOUS")
    if not provenance.reproducibility_metadata:
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "FIXTURE_REPRODUCIBILITY_METADATA_EMPTY")

    metadata_keys = tuple(key for key, _ in provenance.reproducibility_metadata)
    if any(
        not _nonempty(key)
        or not _nonempty(value)
        or _ambiguous(key)
        or _ambiguous(value)
        for key, value in provenance.reproducibility_metadata
    ):
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "FIXTURE_REPRODUCIBILITY_METADATA_INCOMPLETE_OR_AMBIGUOUS")
    if len(set(metadata_keys)) != len(metadata_keys):
        return _invalid(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_REPRODUCIBILITY_METADATA_DUPLICATE_KEY")

    if provenance.contamination_state is ContaminationState.UNKNOWN:
        return _blocked(StopReason.UNKNOWN_PROVENANCE, "FIXTURE_CONTAMINATION_STATE_UNKNOWN")
    if provenance.contamination_state is ContaminationState.CONTAMINATED:
        return _blocked(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_CONTAMINATED")
    if provenance.admissibility_state is not AdmissibilityState.ADMISSIBLE:
        return _blocked(StopReason.FIXTURE_LINEAGE_AMBIGUITY, "FIXTURE_ADMISSIBILITY_NOT_EXPLICIT")

    for input_class in provenance.construction_input_classes:
        if input_class in (InputClassification.UNKNOWN, InputClassification.PROHIBITED):
            return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "FIXTURE_CONSTRUCTION_INPUT_CLASS_PROHIBITED")
        if input_class not in allowed_construction_input_classes:
            return _blocked(StopReason.PROHIBITED_INPUT_CLASS, "FIXTURE_CONSTRUCTION_INPUT_CLASS_NOT_ALLOWED")
    return _valid("FIXTURE_PROVENANCE_VALID")


def validate_role_authorization(
    declaration: RoleDeclaration,
    authorization: ActionAuthorization,
    required_action: Action,
    binding: AuthorityBinding,
    unauthorized_reason: StopReason,
) -> ValidationResult:
    if not _nonempty(declaration.actor_id) or _ambiguous(declaration.actor_id):
        return _blocked(unauthorized_reason, "DECLARED_ACTOR_ID_MISSING_OR_AMBIGUOUS")
    if not _nonempty(authorization.authorization_id) or _ambiguous(
        authorization.authorization_id
    ):
        return _blocked(unauthorized_reason, "ACTION_AUTHORIZATION_ID_MISSING_OR_AMBIGUOUS")
    if declaration.actor_id != authorization.actor_id:
        return _blocked(unauthorized_reason, "ACTION_AUTHORIZATION_ACTOR_MISMATCH")
    if declaration.declared_role is not authorization.declared_role:
        return _blocked(unauthorized_reason, "ACTION_AUTHORIZATION_ROLE_MISMATCH")
    if authorization.action is not required_action:
        return _blocked(unauthorized_reason, "ACTION_AUTHORIZATION_ACTION_MISMATCH")
    if authorization.authority_sha != binding.owner_authority_sha:
        return _blocked(StopReason.AUTHORITY_MISMATCH, "ACTION_AUTHORIZATION_AUTHORITY_MISMATCH")
    if authorization.state is not AuthorizationState.AUTHORIZED:
        return _blocked(unauthorized_reason, "ACTION_AUTHORIZATION_NOT_AUTHORIZED")
    return _valid("ROLE_AND_ACTION_AUTHORIZATION_VALID")


@dataclass(frozen=True, slots=True)
class A2Harness:
    authority: AuthorityBinding
    policy: HarnessPolicy

    def validate_binding(self) -> ValidationResult:
        return validate_authority(self.authority, self.policy)

    def evaluate_input_read(
        self,
        manifest: InputManifest,
        declaration: RoleDeclaration,
        authorization: ActionAuthorization,
    ) -> HarnessDecision:
        authority_result = self.validate_binding()
        if authority_result.state is not ValidationState.VALID:
            return _deny(
                authority_result.stop_reason or StopReason.MISSING_AUTHORITY,
                authority_result.detail_code,
            )

        manifest_result = validate_input_manifest(manifest, self.authority, self.policy)
        if manifest_result.state is not ValidationState.VALID:
            quarantine = (
                QuarantineState.QUARANTINED
                if manifest_result.stop_reason is StopReason.UNEXPECTED_EFFICACY_LEAKAGE
                else QuarantineState.BLOCKED_PENDING_OWNER_REVIEW
            )
            return _deny(
                manifest_result.stop_reason or StopReason.INPUT_MANIFEST_MISMATCH,
                manifest_result.detail_code,
                quarantine,
            )

        if declaration.declared_role not in manifest.permitted_reader_roles:
            return _deny(StopReason.UNAUTHORIZED_READER, "DECLARED_ROLE_NOT_IN_INPUT_READER_ALLOWLIST")

        authorization_result = validate_role_authorization(
            declaration=declaration,
            authorization=authorization,
            required_action=Action.READ_INPUT,
            binding=self.authority,
            unauthorized_reason=StopReason.UNAUTHORIZED_READER,
        )
        if authorization_result.state is not ValidationState.VALID:
            return _deny(
                authorization_result.stop_reason or StopReason.UNAUTHORIZED_READER,
                authorization_result.detail_code,
            )

        return _permit("INPUT_READ_STRUCTURALLY_AUTHORIZED", ReleaseState.BLOCKED)

    def evaluate_fixture_metadata_admission(
        self,
        provenance: FixtureProvenance,
        declaration: RoleDeclaration,
        authorization: ActionAuthorization,
    ) -> HarnessDecision:
        authority_result = self.validate_binding()
        if authority_result.state is not ValidationState.VALID:
            return _deny(
                authority_result.stop_reason or StopReason.MISSING_AUTHORITY,
                authority_result.detail_code,
            )

        provenance_result = validate_fixture_provenance(
            provenance=provenance,
            allowed_construction_input_classes=self.policy.allowed_input_classifications,
        )
        if provenance_result.state is not ValidationState.VALID:
            quarantine = (
                QuarantineState.QUARANTINED
                if provenance_result.stop_reason
                in (StopReason.UNKNOWN_PROVENANCE, StopReason.FIXTURE_LINEAGE_AMBIGUITY)
                else QuarantineState.BLOCKED_PENDING_OWNER_REVIEW
            )
            return _deny(
                provenance_result.stop_reason or StopReason.UNKNOWN_PROVENANCE,
                provenance_result.detail_code,
                quarantine,
            )

        authorization_result = validate_role_authorization(
            declaration=declaration,
            authorization=authorization,
            required_action=Action.ADMIT_FIXTURE_METADATA,
            binding=self.authority,
            unauthorized_reason=StopReason.UNAUTHORIZED_READER,
        )
        if authorization_result.state is not ValidationState.VALID:
            return _deny(
                authorization_result.stop_reason or StopReason.UNAUTHORIZED_READER,
                authorization_result.detail_code,
            )

        return _permit("FIXTURE_METADATA_STRUCTURALLY_ADMISSIBLE", ReleaseState.BLOCKED)

    def evaluate_output_release(
        self,
        manifest: OutputManifest,
        recipient: RoleDeclaration,
        release_actor: RoleDeclaration,
        release_authorization: ActionAuthorization,
        disclosure_ledger: CumulativeDisclosureLedger,
    ) -> HarnessDecision:
        authority_result = self.validate_binding()
        if authority_result.state is not ValidationState.VALID:
            return _deny(
                authority_result.stop_reason or StopReason.MISSING_AUTHORITY,
                authority_result.detail_code,
            )

        manifest_result = validate_output_manifest(manifest, self.authority, self.policy)
        if manifest_result.state is not ValidationState.VALID:
            return _deny(
                manifest_result.stop_reason or StopReason.OUTPUT_MANIFEST_MISMATCH,
                manifest_result.detail_code,
            )

        if recipient.declared_role not in manifest.permitted_recipients:
            return _deny(StopReason.UNAUTHORIZED_RECIPIENT, "DECLARED_ROLE_NOT_IN_OUTPUT_RECIPIENT_ALLOWLIST")
        if not _nonempty(recipient.actor_id) or _ambiguous(recipient.actor_id):
            return _deny(StopReason.UNAUTHORIZED_RECIPIENT, "RECIPIENT_ACTOR_ID_MISSING_OR_AMBIGUOUS")

        if manifest.release_approval_requirement is RequirementState.REQUIRED:
            if release_actor.declared_role is not Role.RELEASE_APPROVER:
                return _deny(StopReason.RELEASE_NOT_AUTHORIZED, "REQUIRED_RELEASE_APPROVER_ROLE_MISSING")

        authorization_result = validate_role_authorization(
            declaration=release_actor,
            authorization=release_authorization,
            required_action=Action.RELEASE_OUTPUT,
            binding=self.authority,
            unauthorized_reason=StopReason.RELEASE_NOT_AUTHORIZED,
        )
        if authorization_result.state is not ValidationState.VALID:
            return _deny(
                authorization_result.stop_reason or StopReason.RELEASE_NOT_AUTHORIZED,
                authorization_result.detail_code,
            )

        if manifest.exportability is not PermissionState.ALLOWED:
            return _deny(StopReason.RELEASE_NOT_AUTHORIZED, "OUTPUT_EXPORTABILITY_NOT_ALLOWED")
        if manifest.quarantine_status is not QuarantineState.CLEAR:
            return _deny(
                StopReason.RELEASE_NOT_AUTHORIZED,
                "OUTPUT_QUARANTINE_STATE_BLOCKS_RELEASE",
                manifest.quarantine_status,
            )
        if manifest.efficacy_leakage_assessment is not LeakageAssessment.CLEAR:
            return _deny(
                StopReason.UNEXPECTED_EFFICACY_LEAKAGE,
                "OUTPUT_EFFICACY_LEAKAGE_NOT_CLEAR",
                QuarantineState.QUARANTINED,
            )
        if manifest.cumulative_disclosure_risk is not CumulativeDisclosureState.CLEAR:
            return _deny(
                StopReason.CUMULATIVE_DISCLOSURE_AMBIGUITY,
                "OUTPUT_MANIFEST_CUMULATIVE_DISCLOSURE_NOT_CLEAR",
            )

        cumulative_state = disclosure_ledger.evaluate_for(
            output_id=manifest.output_id,
            recipient_actor_id=recipient.actor_id,
            recipient_role=recipient.declared_role,
        )
        if cumulative_state is not CumulativeDisclosureState.CLEAR:
            return _deny(
                StopReason.CUMULATIVE_DISCLOSURE_AMBIGUITY,
                "DISCLOSURE_LEDGER_NOT_CLEAR_FOR_EXACT_OUTPUT_AND_RECIPIENT_ACTOR_ROLE",
            )

        if manifest.release_approval_requirement is RequirementState.REQUIRED:
            if release_authorization.state is not AuthorizationState.AUTHORIZED:
                return _deny(StopReason.RELEASE_NOT_AUTHORIZED, "REQUIRED_RELEASE_APPROVAL_NOT_SATISFIED")
        elif manifest.release_approval_requirement is not RequirementState.NOT_REQUIRED:
            return _deny(StopReason.RELEASE_NOT_AUTHORIZED, "RELEASE_APPROVAL_REQUIREMENT_NOT_RESOLVED")

        return _permit("OUTPUT_RELEASE_STRUCTURALLY_AUTHORIZED", ReleaseState.AUTHORIZED)

    def evaluate_resource_boundary(
        self,
        state: ResourceBoundaryState,
    ) -> HarnessDecision:
        authority_result = self.validate_binding()
        if authority_result.state is not ValidationState.VALID:
            return _deny(
                authority_result.stop_reason or StopReason.MISSING_AUTHORITY,
                authority_result.detail_code,
            )
        if state is not ResourceBoundaryState.WITHIN_AUTHORITY:
            return _deny(
                StopReason.RESOURCE_BOUNDARY_UNRESOLVED,
                "RESOURCE_BOUNDARY_NOT_EXPLICITLY_WITHIN_AUTHORITY",
            )
        return _permit("RESOURCE_BOUNDARY_WITHIN_AUTHORITY", ReleaseState.BLOCKED)

    def stop_for_unexpected_efficacy_leakage(self) -> HarnessDecision:
        return _deny(
            StopReason.UNEXPECTED_EFFICACY_LEAKAGE,
            "UNEXPECTED_EFFICACY_LEAKAGE_FAIL_CLOSED_STOP",
            QuarantineState.QUARANTINED,
        )

    def append_log_record(
        self,
        log: StructuredAuditLog,
        record_id: str,
        manifest_identity: str,
        actor_role: RoleDeclaration,
        attempted_action: Action,
        decision: HarnessDecision,
        incident_identifier: str,
        cumulative_disclosure_state: CumulativeDisclosureState,
    ) -> StructuredAuditLog:
        record = LogRecord(
            record_id=record_id,
            authority_identity=self.authority.owner_authority_sha,
            manifest_identity=manifest_identity,
            actor_role=actor_role.declared_role,
            attempted_action=attempted_action,
            permit_or_deny_state=decision.permit_or_deny_state,
            quarantine_state=decision.quarantine_state,
            release_state=decision.release_state,
            incident_identifier=incident_identifier,
            cumulative_disclosure_state=cumulative_disclosure_state,
        )
        return log.append(record)
