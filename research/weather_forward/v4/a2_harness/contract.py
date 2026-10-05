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


class CompletionState(str, Enum):
    COMPLETED = "COMPLETED"
    NOT_COMPLETED = "NOT_COMPLETED"


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


class TargetKind(str, Enum):
    INPUT_MANIFEST = "INPUT_MANIFEST"
    FIXTURE_PROVENANCE = "FIXTURE_PROVENANCE"
    OUTPUT_MANIFEST = "OUTPUT_MANIFEST"


class StopReason(str, Enum):
    MISSING_AUTHORITY = "MISSING_AUTHORITY"
    MISSING_EXECUTION_POLICY_ROOT = "MISSING_EXECUTION_POLICY_ROOT"
    EXECUTION_POLICY_ROOT_MISMATCH = "EXECUTION_POLICY_ROOT_MISMATCH"
    AUTHORITY_MISMATCH = "AUTHORITY_MISMATCH"
    UNKNOWN_PROVENANCE = "UNKNOWN_PROVENANCE"
    PROHIBITED_INPUT_CLASS = "PROHIBITED_INPUT_CLASS"
    INPUT_MANIFEST_MISMATCH = "INPUT_MANIFEST_MISMATCH"
    OUTPUT_MANIFEST_MISMATCH = "OUTPUT_MANIFEST_MISMATCH"
    UNAUTHORIZED_READER = "UNAUTHORIZED_READER"
    UNAUTHORIZED_RECIPIENT = "UNAUTHORIZED_RECIPIENT"
    FIXTURE_LINEAGE_AMBIGUITY = "FIXTURE_LINEAGE_AMBIGUITY"
    FIXTURE_PROVENANCE_MISMATCH = "FIXTURE_PROVENANCE_MISMATCH"
    UNEXPECTED_EFFICACY_LEAKAGE = "UNEXPECTED_EFFICACY_LEAKAGE"
    CUMULATIVE_DISCLOSURE_AMBIGUITY = "CUMULATIVE_DISCLOSURE_AMBIGUITY"
    RESOURCE_BOUNDARY_UNRESOLVED = "RESOURCE_BOUNDARY_UNRESOLVED"
    RELEASE_NOT_AUTHORIZED = "RELEASE_NOT_AUTHORIZED"
    RELEASE_INDEPENDENCE_VIOLATION = "RELEASE_INDEPENDENCE_VIOLATION"
    LOGGING_REQUIRED = "LOGGING_REQUIRED"
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
class FixtureProvenanceContract:
    expected_fixture_id: str
    expected_generator_identity: str
    expected_generator_version: str
    expected_construction_input_classes: tuple[InputClassification, ...]
    expected_lineage_references: tuple[str, ...]
    required_reproducibility_keys: tuple[str, ...]
    allowed_reproducibility_keys: tuple[str, ...]
    expected_fixture_provenance_identity: str


@dataclass(frozen=True, slots=True)
class TrustedExecutionPolicyRoot:
    execution_policy_authority_sha: str
    expected_construction_authority_sha: str
    expected_harness_identity: str
    expected_harness_version_or_commit_identity: str
    expected_policy_identity: str


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
    construction_authority_identity: str
    execution_policy_authority_identity: str | None
    authorization_authority_identity: str
    manifest_identity: str
    actor_id: str
    actor_role: Role
    authorization_id: str
    attempted_action: Action
    target_kind: TargetKind
    target_id: str
    permit_or_deny_state: PermitState
    quarantine_state: QuarantineState
    release_state: ReleaseState
    incident_identifier: str | None
    cumulative_disclosure_state: CumulativeDisclosureState | None
    recipient_actor_id: str | None
    recipient_role: Role | None


@dataclass(frozen=True, slots=True)
class LogAppendAcknowledgement:
    appended: bool
    record_id: str
    log: "StructuredAuditLog"


@dataclass(frozen=True, slots=True)
class StructuredAuditLog:
    records: tuple[LogRecord, ...]

    def append(self, record: LogRecord) -> LogAppendAcknowledgement:
        if not record.record_id or not record.record_id.strip():
            return LogAppendAcknowledgement(False, record.record_id, self)
        if any(existing.record_id == record.record_id for existing in self.records):
            return LogAppendAcknowledgement(False, record.record_id, self)
        updated = StructuredAuditLog(records=self.records + (record,))
        return LogAppendAcknowledgement(True, record.record_id, updated)


_AMBIGUOUS_RECIPIENT_IDENTITIES = frozenset(
    {"UNKNOWN", "UNRESOLVED", "AMBIGUOUS", "NOT_ATTESTED"}
)


def _recipient_identity_is_resolved(actor_id: str) -> bool:
    return bool(
        actor_id
        and actor_id.strip()
        and actor_id.strip().upper() not in _AMBIGUOUS_RECIPIENT_IDENTITIES
    )


@dataclass(frozen=True, slots=True)
class DisclosureRecord:
    disclosure_id: str
    output_id: str
    recipient_actor_id: str
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
            not _recipient_identity_is_resolved(record.recipient_actor_id)
            for record in self.records
        ):
            return CumulativeDisclosureState.UNRESOLVED
        if any(
            record.cumulative_safety is CumulativeDisclosureState.UNRESOLVED
            for record in self.records
        ):
            return CumulativeDisclosureState.UNRESOLVED
        return CumulativeDisclosureState.CLEAR

    def evaluate_for(
        self,
        output_id: str,
        recipient_actor_id: str,
        recipient_role: Role,
    ) -> CumulativeDisclosureState:
        overall = self.evaluate()
        if overall is not CumulativeDisclosureState.CLEAR:
            return overall

        if not _recipient_identity_is_resolved(recipient_actor_id):
            return CumulativeDisclosureState.UNRESOLVED

        relevant_records = tuple(
            record
            for record in self.records
            if record.output_id == output_id
            and record.recipient_actor_id == recipient_actor_id
            and record.recipient_role is recipient_role
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


def _decision_is_permissive(
    permit_or_deny_state: PermitState,
    release_state: ReleaseState,
) -> bool:
    return (
        permit_or_deny_state is PermitState.PERMIT
        or release_state is ReleaseState.AUTHORIZED
    )


@dataclass(frozen=True, slots=True, init=False)
class HarnessDecision:
    """Public decision model with denial-only direct construction."""

    validation_state: ValidationState
    permit_or_deny_state: PermitState
    quarantine_state: QuarantineState
    release_state: ReleaseState
    completion_state: CompletionState
    stop_reason: StopReason | None
    detail_code: str

    def __init__(
        self,
        validation_state: ValidationState,
        permit_or_deny_state: PermitState,
        quarantine_state: QuarantineState,
        release_state: ReleaseState,
        completion_state: CompletionState,
        stop_reason: StopReason | None,
        detail_code: str,
    ) -> None:
        if _decision_is_permissive(permit_or_deny_state, release_state):
            raise ValueError(
                "FINAL_PERMISSIVE_HARNESS_DECISION_REQUIRES_ACKNOWLEDGED_LOG_FINALIZATION"
            )
        object.__setattr__(self, "validation_state", validation_state)
        object.__setattr__(self, "permit_or_deny_state", permit_or_deny_state)
        object.__setattr__(self, "quarantine_state", quarantine_state)
        object.__setattr__(self, "release_state", release_state)
        object.__setattr__(self, "completion_state", completion_state)
        object.__setattr__(self, "stop_reason", stop_reason)
        object.__setattr__(self, "detail_code", detail_code)


def _new_guarded_harness_decision(
    *,
    validation_state: ValidationState,
    permit_or_deny_state: PermitState,
    quarantine_state: QuarantineState,
    release_state: ReleaseState,
    completion_state: CompletionState,
    stop_reason: StopReason | None,
    detail_code: str,
) -> HarnessDecision:
    decision = object.__new__(HarnessDecision)
    object.__setattr__(decision, "validation_state", validation_state)
    object.__setattr__(decision, "permit_or_deny_state", permit_or_deny_state)
    object.__setattr__(decision, "quarantine_state", quarantine_state)
    object.__setattr__(decision, "release_state", release_state)
    object.__setattr__(decision, "completion_state", completion_state)
    object.__setattr__(decision, "stop_reason", stop_reason)
    object.__setattr__(decision, "detail_code", detail_code)
    return decision


@dataclass(frozen=True, slots=True, init=False)
class LoggedActionResult:
    """Public final action result with guarded permissive construction."""

    decision: HarnessDecision
    log: StructuredAuditLog
    log_record: LogRecord | None
    log_acknowledged: bool

    def __init__(
        self,
        decision: HarnessDecision,
        log: StructuredAuditLog,
        log_record: LogRecord | None,
        log_acknowledged: bool,
    ) -> None:
        if _decision_is_permissive(
            decision.permit_or_deny_state,
            decision.release_state,
        ):
            raise ValueError(
                "PERMISSIVE_LOGGED_ACTION_RESULT_REQUIRES_GUARDED_FINALIZER"
            )
        if log_acknowledged or log_record is not None:
            raise ValueError(
                "ACKNOWLEDGED_LOG_LINK_REQUIRES_GUARDED_FINALIZER"
            )
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "log", log)
        object.__setattr__(self, "log_record", None)
        object.__setattr__(self, "log_acknowledged", False)


def _finalize_logged_action_result(
    *,
    acknowledgement: LogAppendAcknowledgement,
    log_record: LogRecord,
    validation_state: ValidationState,
    permit_or_deny_state: PermitState,
    quarantine_state: QuarantineState,
    release_state: ReleaseState,
    completion_state: CompletionState,
    stop_reason: StopReason | None,
    detail_code: str,
    expected_construction_authority_identity: str,
    expected_execution_policy_authority_identity: str | None,
    expected_actor: RoleDeclaration,
    expected_authorization: ActionAuthorization,
    expected_action: Action,
    expected_target_kind: TargetKind,
    expected_target_id: str,
    expected_manifest_identity: str,
    expected_incident_identifier: str | None,
    expected_cumulative_disclosure_state: CumulativeDisclosureState | None,
    expected_recipient: RoleDeclaration | None,
) -> LoggedActionResult | None:
    """Private exact acknowledged-log finalizer for authority-bearing actions."""

    if not acknowledgement.appended:
        return None
    if acknowledgement.record_id != log_record.record_id:
        return None

    matching_records = tuple(
        record
        for record in acknowledgement.log.records
        if record.record_id == log_record.record_id
    )
    if len(matching_records) != 1:
        return None
    if matching_records[0] != log_record:
        return None

    expected_recipient_actor_id = (
        expected_recipient.actor_id if expected_recipient is not None else None
    )
    expected_recipient_role = (
        expected_recipient.declared_role if expected_recipient is not None else None
    )

    if log_record.construction_authority_identity != expected_construction_authority_identity:
        return None
    if log_record.execution_policy_authority_identity != expected_execution_policy_authority_identity:
        return None
    if log_record.authorization_authority_identity != expected_authorization.authority_sha:
        return None
    if log_record.actor_id != expected_actor.actor_id:
        return None
    if log_record.actor_role is not expected_actor.declared_role:
        return None
    if log_record.authorization_id != expected_authorization.authorization_id:
        return None
    if log_record.attempted_action is not expected_action:
        return None
    if log_record.target_kind is not expected_target_kind:
        return None
    if log_record.target_id != expected_target_id:
        return None
    if log_record.manifest_identity != expected_manifest_identity:
        return None
    if log_record.incident_identifier != expected_incident_identifier:
        return None
    if log_record.cumulative_disclosure_state is not expected_cumulative_disclosure_state:
        return None
    if log_record.recipient_actor_id != expected_recipient_actor_id:
        return None
    if log_record.recipient_role is not expected_recipient_role:
        return None

    if log_record.permit_or_deny_state is not permit_or_deny_state:
        return None
    if log_record.quarantine_state is not quarantine_state:
        return None
    if log_record.release_state is not release_state:
        return None

    permissive = _decision_is_permissive(permit_or_deny_state, release_state)
    if release_state is ReleaseState.AUTHORIZED and permit_or_deny_state is not PermitState.PERMIT:
        return None
    if permit_or_deny_state is PermitState.DENY and release_state is not ReleaseState.BLOCKED:
        return None
    if permissive:
        if completion_state is not CompletionState.COMPLETED:
            return None
        if validation_state is not ValidationState.VALID:
            return None

    decision = _new_guarded_harness_decision(
        validation_state=validation_state,
        permit_or_deny_state=permit_or_deny_state,
        quarantine_state=quarantine_state,
        release_state=release_state,
        completion_state=completion_state,
        stop_reason=stop_reason,
        detail_code=detail_code,
    )

    result = object.__new__(LoggedActionResult)
    object.__setattr__(result, "decision", decision)
    object.__setattr__(result, "log", acknowledgement.log)
    object.__setattr__(result, "log_record", log_record)
    object.__setattr__(result, "log_acknowledged", True)
    return result
