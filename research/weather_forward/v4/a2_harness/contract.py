from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ValidationState(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    BLOCKED = "BLOCKED"


class PermitState(str, Enum):
    PERMIT = "PERMIT"
    DENY = "DENY"


class ReleaseState(str, Enum):
    BLOCKED = "BLOCKED"
    AUTHORIZED = "AUTHORIZED"


class QuarantineState(str, Enum):
    CLEAR = "CLEAR"
    QUARANTINED = "QUARANTINED"
    BLOCKED_PENDING_OWNER_REVIEW = "BLOCKED_PENDING_OWNER_REVIEW"


class CumulativeDisclosureState(str, Enum):
    CLEAR = "CLEAR"
    UNRESOLVED = "UNRESOLVED"
    BLOCKED = "BLOCKED"


class LeakageAssessment(str, Enum):
    CLEAR = "CLEAR"
    UNRESOLVED = "UNRESOLVED"
    BLOCKED = "BLOCKED"


class VisibilityState(str, Enum):
    VISIBLE = "VISIBLE"
    HIDDEN = "HIDDEN"
    UNRESOLVED = "UNRESOLVED"


class PermissionState(str, Enum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    UNRESOLVED = "UNRESOLVED"


class RequirementState(str, Enum):
    REQUIRED = "REQUIRED"
    NOT_REQUIRED = "NOT_REQUIRED"
    UNRESOLVED = "UNRESOLVED"


class AuthorizationState(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"
    UNRESOLVED = "UNRESOLVED"


class ResourceBoundaryState(str, Enum):
    WITHIN_AUTHORITY = "WITHIN_AUTHORITY"
    UNRESOLVED = "UNRESOLVED"
    EXCEEDED = "EXCEEDED"


class InputClassification(str, Enum):
    DOCUMENTATION_ONLY = "DOCUMENTATION_ONLY"
    NON_ECONOMIC_SYNTHETIC = "NON_ECONOMIC_SYNTHETIC"
    REAL_TECHNICAL_METADATA = "REAL_TECHNICAL_METADATA"
    PROHIBITED = "PROHIBITED"
    UNKNOWN = "UNKNOWN"


class ContaminationState(str, Enum):
    CLEAR = "CLEAR"
    UNKNOWN = "UNKNOWN"
    CONTAMINATED = "CONTAMINATED"


class AdmissibilityState(str, Enum):
    ADMISSIBLE = "ADMISSIBLE"
    UNRESOLVED = "UNRESOLVED"
    BLOCKED = "BLOCKED"


class Role(str, Enum):
    PHASE_OWNER = "PHASE_OWNER"
    EXECUTOR = "EXECUTOR"
    CUSTODY_ADMIN = "CUSTODY_ADMIN"
    RESEARCH_VIEWER = "RESEARCH_VIEWER"
    RELEASE_APPROVER = "RELEASE_APPROVER"
    INCIDENT_AUTHORITY = "INCIDENT_AUTHORITY"


class Action(str, Enum):
    READ_INPUT = "READ_INPUT"
    ADMIT_FIXTURE_METADATA = "ADMIT_FIXTURE_METADATA"
    RELEASE_OUTPUT = "RELEASE_OUTPUT"
    RECORD_LOG = "RECORD_LOG"
    HANDLE_INCIDENT = "HANDLE_INCIDENT"


class StopReason(str, Enum):
    MISSING_AUTHORITY = "MISSING_AUTHORITY"
    AUTHORITY_MISMATCH = "AUTHORITY_MISMATCH"
    UNKNOWN_PROVENANCE = "UNKNOWN_PROVENANCE"
    PROHIBITED_INPUT_CLASS = "PROHIBITED_INPUT_CLASS"
    INPUT_MANIFEST_MISMATCH = "INPUT_MANIFEST_MISMATCH"
    OUTPUT_MANIFEST_MISMATCH = "OUTPUT_MANIFEST_MISMATCH"
    UNAUTHORIZED_READER = "UNAUTHORIZED_READER"
    UNAUTHORIZED_RECIPIENT = "UNAUTHORIZED_RECIPIENT"
    FIXTURE_LINEAGE_AMBIGUITY = "FIXTURE_LINEAGE_AMBIGUITY"
    UNEXPECTED_EFFICACY_LEAKAGE = "UNEXPECTED_EFFICACY_LEAKAGE"
    CUMULATIVE_DISCLOSURE_AMBIGUITY = "CUMULATIVE_DISCLOSURE_AMBIGUITY"
    RESOURCE_BOUNDARY_UNRESOLVED = "RESOURCE_BOUNDARY_UNRESOLVED"
    RELEASE_NOT_AUTHORIZED = "RELEASE_NOT_AUTHORIZED"
    INVALID_DECLARATION = "INVALID_DECLARATION"


@dataclass(frozen=True, slots=True)
class AuthorityBinding:
    owner_authority_sha: str
    harness_identity: str
    harness_version_or_commit_identity: str
    manifest_version_identity: str


@dataclass(frozen=True, slots=True)
class InputManifest:
    input_id: str
    manifest_version_identity: str
    input_classification: InputClassification
    source_provenance_class: str
    exact_permitted_fields: tuple[str, ...]
    exact_prohibited_fields: tuple[str, ...]
    permitted_reader_roles: tuple[Role, ...]
    raw_values_visible: VisibilityState
    timestamps_visible: VisibilityState
    frequency_or_count_information_visible: VisibilityState
    longitudinal_observation_allowed: PermissionState
    aggregation_allowed: PermissionState
    cross_source_comparison_allowed: PermissionState
    efficacy_leakage_assessment: LeakageAssessment
    access_logging_requirement: RequirementState
    quarantine_on_ambiguity: RequirementState
    owner_approval_required: RequirementState


@dataclass(frozen=True, slots=True)
class OutputManifest:
    output_id: str
    manifest_version_identity: str
    output_type: str
    exact_metric_or_artifact: str
    granularity: str
    permitted_recipients: tuple[Role, ...]
    exportability: PermissionState
    quarantine_status: QuarantineState
    cumulative_disclosure_risk: CumulativeDisclosureState
    efficacy_leakage_assessment: LeakageAssessment
    release_approval_requirement: RequirementState
    retention_rule: str
    incident_if_unexpected_information_revealed: str


@dataclass(frozen=True, slots=True)
class FixtureProvenance:
    fixture_id: str
    construction_input_classes: tuple[InputClassification, ...]
    generator_identity: str
    generator_version: str
    lineage_references: tuple[str, ...]
    reproducibility_metadata: tuple[tuple[str, str], ...]
    contamination_state: ContaminationState
    admissibility_state: AdmissibilityState


@dataclass(frozen=True, slots=True)
class RoleDeclaration:
    actor_id: str
    declared_role: Role


@dataclass(frozen=True, slots=True)
class ActionAuthorization:
    authorization_id: str
    authority_sha: str
    actor_id: str
    declared_role: Role
    action: Action
    state: AuthorizationState


@dataclass(frozen=True, slots=True)
class LogRecord:
    record_id: str
    authority_identity: str
    manifest_identity: str
    actor_role: Role
    attempted_action: Action
    permit_or_deny_state: PermitState
    quarantine_state: QuarantineState
    release_state: ReleaseState
    incident_identifier: str
    cumulative_disclosure_state: CumulativeDisclosureState


@dataclass(frozen=True, slots=True)
class StructuredAuditLog:
    records: tuple[LogRecord, ...]

    def append(self, record: LogRecord) -> "StructuredAuditLog":
        return StructuredAuditLog(records=self.records + (record,))


@dataclass(frozen=True, slots=True)
class DisclosureRecord:
    disclosure_id: str
    output_id: str
    recipient_role: Role
    cumulative_safety: CumulativeDisclosureState


@dataclass(frozen=True, slots=True)
class CumulativeDisclosureLedger:
    records: tuple[DisclosureRecord, ...]

    def evaluate(self) -> CumulativeDisclosureState:
        if not self.records:
            return CumulativeDisclosureState.UNRESOLVED
        if any(
            record.cumulative_safety is CumulativeDisclosureState.BLOCKED
            for record in self.records
        ):
            return CumulativeDisclosureState.BLOCKED
        if any(
            record.cumulative_safety is CumulativeDisclosureState.UNRESOLVED
            for record in self.records
        ):
            return CumulativeDisclosureState.UNRESOLVED
        return CumulativeDisclosureState.CLEAR

    def evaluate_for(
        self,
        output_id: str,
        recipient_role: Role,
    ) -> CumulativeDisclosureState:
        overall = self.evaluate()
        if overall is not CumulativeDisclosureState.CLEAR:
            return overall
        relevant_records = tuple(
            record
            for record in self.records
            if record.output_id == output_id and record.recipient_role is recipient_role
        )
        if not relevant_records:
            return CumulativeDisclosureState.UNRESOLVED
        if any(
            record.cumulative_safety is not CumulativeDisclosureState.CLEAR
            for record in relevant_records
        ):
            return CumulativeDisclosureState.BLOCKED
        return CumulativeDisclosureState.CLEAR


@dataclass(frozen=True, slots=True)
class ValidationResult:
    state: ValidationState
    stop_reason: StopReason | None
    detail_code: str


@dataclass(frozen=True, slots=True)
class HarnessDecision:
    validation_state: ValidationState
    permit_or_deny_state: PermitState
    quarantine_state: QuarantineState
    release_state: ReleaseState
    stop_reason: StopReason | None
    detail_code: str
