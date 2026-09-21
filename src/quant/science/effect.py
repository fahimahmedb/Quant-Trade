"""First-vertical Form-4 scientific effect authority.

This module implements the frozen FORM4_FIRST_VERTICAL_MULTI_COHORT_V1
scientific producer. It deliberately keeps structural stopping separate from
target outcomes: structural_stopping_decision has no outcome argument.

The module is bounded to the first vertical slice. It does not create a second
research framework, scheduler, sizing engine, execution engine, or Book.
"""

from __future__ import annotations

import hashlib
import inspect
import itertools
import math
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from ..economics.coordinate import (
    ALLOCATION_WEIGHTED_RATIO,
    DeltaCoordinateBinding,
    ReturnConvention,
    evaluate_delta_coordinate,
)
from ..economics.decision import (
    EVIDENCE_DEVELOPMENT,
    EVIDENCE_FORWARD_CONFIRMATION,
    EffectEstimate,
)
from ..economics.fingerprint import canonical_json, recipe_hash
from ..economics.states import (
    CLUSTERING_UNIT_O4_RESOLVED,
    DELTA_COORDINATE_MISMATCH,
    DELTA_COORDINATE_UNRESOLVED,
)
from ..state import read_json, write_json
from .formation import SessionCalendar
from .inference import ratio_estimate


PROTOCOL_ID = "FORM4_FIRST_VERTICAL_MULTI_COHORT_V1"
ENTRY_SESSIONS_PER_COHORT = 252
K_TARGET = 3
K_MAX = 4
INTER_COHORT_SEPARATION = 80
G_MIN = 10
MAX_COMPONENT_EXPOSURE_SHARE = 0.10
FAMILY_ALPHA = 0.05
CONFIDENCE_LEVEL = 0.95

REFERENCE_CAPITAL = 10_000.0
SLOT_COUNT = 20
PARTICIPATION_CEILING = 0.001
PER_SLOT_CAP = REFERENCE_CAPITAL / SLOT_COUNT
ALLOCATION_CONSTRUCTOR_NAME = "FORM4_SLOT20_ADV20_V1"

HOLDING_SESSIONS = 20
INFLUENCE_LEAD_SESSIONS = 40
INFLUENCE_POST_SESSIONS = 20

INTERVAL_METHOD_ID = "WILD_CLUSTER_RADEMACHER_RATIO_V1"
INTERVAL_ALGORITHM_ID = "COMPONENT_SCORE_SIGN_FLIP_OVER_ALLOCATION_WEIGHTED_RATIO"
QUALIFICATION_VERSION = "FORM4_RADEMACHER_QUALIFICATION_V1"
DEFAULT_SIGN_SEED = 20260921
DEFAULT_SIGN_DRAWS = 9999
EXHAUSTIVE_COMPONENT_LIMIT = 20

STRUCTURAL_CONTINUE = "ACCRUE_NEXT_COHORT"
STRUCTURAL_INFERENCE_ELIGIBLE = "INFERENCE_ELIGIBLE"
STRUCTURAL_INSUFFICIENT = "INSUFFICIENT_CLUSTER_INFORMATION"

WAITING_FOR_OUTCOME = "WAITING_FOR_OUTCOME"
DEPENDENCE_MODEL_UNSUPPORTED = "DEPENDENCE_MODEL_UNSUPPORTED"
D19_INSUFFICIENT = "D19_INSUFFICIENT_UNRESOLVED_COMPLETIONS"
EFFECT_UNAVAILABLE = "EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE"
PROTOCOL_MISMATCH = "COHORT_PROTOCOL_HASH_MISMATCH"
COHORT_GAP_VIOLATION = "INTER_COHORT_SEPARATION_LT_80"
FIFTH_COHORT_REFUSED = "K_MAX_FOUR_NO_FIFTH_COHORT"
CONCENTRATION_GUARD_FAILED = "COMPONENT_EXPOSURE_CONCENTRATION_EXCEEDS_0_10"
INSUFFICIENT_G = "POSITIVE_EXPOSURE_COMPONENT_COUNT_BELOW_10"
INVALID_SCIENTIFIC_INPUT = "INVALID_SCIENTIFIC_INPUT"

RETURN_DEFINITION = "SIMPLE_SINGLE_PERIOD"
INTERVAL_SPEC = "PUBLIC_KNOWLEDGE_NEXT_OPEN_TO_20TH_CLOSE_V1"
CORPORATE_ACTION_CONVENTION = "SHARE_ENTITLEMENTS_PLUS_UNREINVESTED_CASH_V1"
TERMINAL_TREATMENT = "VERIFIED_ENTITLEMENTS_ELSE_D19_INSUFFICIENT_V1"
D19_REFERENCE = (
    "governance/BLUE_RESEARCH_FROZEN_EFFECT_ESTIMATE_PRESTAGE_2026-09-21.md"
    "#103-returns-corporate-actions-and-d19"
)


def _sha256_document(document: Any) -> str:
    return "sha256:" + hashlib.sha256(
        canonical_json(document).encode("utf-8")
    ).hexdigest()


def _finite_nonnegative(value: float) -> bool:
    return math.isfinite(float(value)) and float(value) >= 0.0


def _finite(value: float) -> bool:
    return math.isfinite(float(value))


ALLOCATION_RULE_DOCUMENT = {
    "schema_version": 1,
    "constructor": ALLOCATION_CONSTRUCTOR_NAME,
    "reference_capital_usd": "10000",
    "slot_count": SLOT_COUNT,
    "per_slot_cap_usd": "500",
    "participation_ceiling_of_adv20": "0.001",
    "adv20_sessions": 20,
    "ordering": ["entry_session", "issuer_cik", "security_id", "crossing_id"],
    "slot_release": "scheduled_exit_strictly_before_next_entry",
    "same_issuer_active_slot": "ZERO_ALLOCATION",
    "full_slot_book": "ZERO_ALLOCATION",
    "outcome_inputs": "FORBIDDEN",
}
ALLOCATION_RULE_HASH = recipe_hash(ALLOCATION_RULE_DOCUMENT)
ALLOCATION_CONSTRUCTOR_ID = f"{ALLOCATION_CONSTRUCTOR_NAME}:{ALLOCATION_RULE_HASH}"


@dataclass(frozen=True)
class ProtocolConfig:
    protocol_id: str = PROTOCOL_ID
    entry_sessions_per_cohort: int = ENTRY_SESSIONS_PER_COHORT
    k_target: int = K_TARGET
    k_max: int = K_MAX
    inter_cohort_separation: int = INTER_COHORT_SEPARATION
    g_min: int = G_MIN
    max_component_exposure_share: float = MAX_COMPONENT_EXPOSURE_SHARE
    family_alpha: float = FAMILY_ALPHA
    interval_method_id: str = INTERVAL_METHOD_ID
    influence_lead_sessions: int = INFLUENCE_LEAD_SESSIONS
    influence_post_sessions: int = INFLUENCE_POST_SESSIONS
    allocation_constructor_id: str = ALLOCATION_CONSTRUCTOR_ID

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def protocol_hash(self) -> str:
        return recipe_hash(self.to_dict())

    def violations(self) -> tuple[str, ...]:
        expected = ProtocolConfig()
        if self == expected:
            return ()
        return ("FROZEN_PROTOCOL_CONFIGURATION_CHANGED",)


@dataclass(frozen=True)
class AllocationCandidate:
    """Pre-outcome input to the frozen scientific reference allocation policy."""

    event_id: str
    issuer_cik: str
    security_id: str
    crossing_id: str
    entry_session: str
    adv20_usd: float
    content_addresses: tuple[str, ...] = ()


@dataclass(frozen=True)
class StructuralEvent:
    """Outcome-free event state used by cohort stopping and dependence geometry."""

    event_id: str
    issuer_cik: str
    security_id: str
    crossing_id: str
    entry_session: str
    scheduled_exit_session: str
    allocation_weight: float
    adv20_usd: float
    allocation_slot: int | None
    allocation_reason: str
    allocation_commitment_hash: str
    content_addresses: tuple[str, ...] = ()
    corporate_group: str | None = None
    d19_complete: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CohortRecord:
    cohort_id: str
    ordinal: int
    first_entry_session: str
    last_entry_session: str
    matured: bool
    protocol_hash: str
    events: tuple[StructuralEvent, ...]
    source_manifest_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "cohort_id": self.cohort_id,
            "ordinal": self.ordinal,
            "first_entry_session": self.first_entry_session,
            "last_entry_session": self.last_entry_session,
            "matured": self.matured,
            "protocol_hash": self.protocol_hash,
            "events": [event.to_dict() for event in self.events],
            "source_manifest_hash": self.source_manifest_hash,
        }


@dataclass(frozen=True)
class StructuralStoppingDecision:
    state: str
    reasons: tuple[str, ...]
    cohort_count: int
    matured_cohort_count: int
    positive_exposure_components: int
    total_positive_exposure: float
    max_component_exposure_share: float | None
    component_assignments: tuple[tuple[str, str], ...]
    component_exposures: tuple[tuple[str, float], ...]

    @property
    def inference_eligible(self) -> bool:
        return self.state == STRUCTURAL_INFERENCE_ELIGIBLE

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "reasons": list(self.reasons),
            "cohort_count": self.cohort_count,
            "matured_cohort_count": self.matured_cohort_count,
            "positive_exposure_components": self.positive_exposure_components,
            "total_positive_exposure": self.total_positive_exposure,
            "max_component_exposure_share": self.max_component_exposure_share,
            "component_assignments": [list(item) for item in self.component_assignments],
            "component_exposures": [list(item) for item in self.component_exposures],
        }


@dataclass(frozen=True)
class SignFlipInterval:
    state: str
    point: float | None
    lower: float | None
    upper: float | None
    confidence_level: float
    method_id: str
    component_count: int
    observations: int
    denominator: float
    enumeration: str
    draws: int
    seed: int | None
    detail: str = ""

    @property
    def resolved(self) -> bool:
        return (
            self.state == "ESTIMATE_RESOLVED"
            and self.point is not None
            and self.lower is not None
            and self.upper is not None
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QualificationStressResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class MethodQualificationArtifact:
    qualification_id: str
    protocol_id: str
    protocol_hash: str
    method_id: str
    method_version: str
    algorithm_id: str
    runtime_identity: str
    confidence_level: float
    random_denominator_treatment: str
    component_definition: str
    enumeration_rule: str
    declared_dependence_assumptions: tuple[str, ...]
    concentration_guard: str
    fixture_identity: str
    stress_results: tuple[QualificationStressResult, ...]
    numerical_qualification_passed: bool
    target_cohort_applicability_supported: bool
    applicability_evidence_hash: str | None
    applicability_statement: str
    limitations: tuple[str, ...]
    synthetic_only: bool = True

    @property
    def qualified_for_forward_confirmation(self) -> bool:
        return (
            self.numerical_qualification_passed
            and self.target_cohort_applicability_supported
            and bool(self.applicability_evidence_hash)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            **{
                key: value
                for key, value in asdict(self).items()
                if key != "stress_results"
            },
            "stress_results": [asdict(item) for item in self.stress_results],
            "qualified_for_forward_confirmation": self.qualified_for_forward_confirmation,
        }


@dataclass(frozen=True)
class ForwardConfirmationReceipt:
    """M1-side typed receipt. M2 derives this from canonical admissibility/use state."""

    receipt_id: str
    protocol_hash: str
    sample_id: str
    evidence_identity: str
    session_seals_hash: str
    allocation_seal_hash: str
    use_ledger_receipt: str
    family_look_receipt: str
    post_freeze_recording_proven: bool
    evidence_unconsumed: bool
    source: str = "CANONICAL_FORWARD_ADMISSIBILITY"

    def valid_for(self, protocol_hash: str, sample_id: str) -> bool:
        return (
            self.protocol_hash == protocol_hash
            and self.sample_id == sample_id
            and bool(self.receipt_id)
            and bool(self.evidence_identity)
            and bool(self.session_seals_hash)
            and bool(self.allocation_seal_hash)
            and bool(self.use_ledger_receipt)
            and bool(self.family_look_receipt)
            and self.post_freeze_recording_proven
            and self.evidence_unconsumed
            and self.source == "CANONICAL_FORWARD_ADMISSIBILITY"
        )


@dataclass(frozen=True)
class ScientificEffectArtifact:
    status: str
    reason_codes: tuple[str, ...]
    protocol_id: str
    protocol_hash: str
    sample_id: str
    cohort_ids: tuple[str, ...]
    sample_provenance: str
    allocation_constructor_id: str
    allocation_commitment_hashes: tuple[str, ...]
    component_assignments: tuple[tuple[str, str], ...]
    d19_complete: bool
    method_qualification_id: str | None
    method_qualification_hash: str | None
    delta_coordinate_binding: DeltaCoordinateBinding | None
    delta_coordinate_hash: str | None
    evidence_label: str
    point: float | None
    lower: float | None
    upper: float | None
    confidence_level: float
    event_count: int
    interval_method_id: str | None
    synthetic: bool
    effect_estimate: EffectEstimate | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "protocol_id": self.protocol_id,
            "protocol_hash": self.protocol_hash,
            "sample_id": self.sample_id,
            "cohort_ids": list(self.cohort_ids),
            "sample_provenance": self.sample_provenance,
            "allocation_constructor_id": self.allocation_constructor_id,
            "allocation_commitment_hashes": list(self.allocation_commitment_hashes),
            "component_assignments": [list(item) for item in self.component_assignments],
            "d19_complete": self.d19_complete,
            "method_qualification_id": self.method_qualification_id,
            "method_qualification_hash": self.method_qualification_hash,
            "delta_coordinate_binding": (
                self.delta_coordinate_binding.to_dict()
                if self.delta_coordinate_binding is not None else None
            ),
            "delta_coordinate_hash": self.delta_coordinate_hash,
            "evidence_label": self.evidence_label,
            "point": self.point,
            "lower": self.lower,
            "upper": self.upper,
            "confidence_level": self.confidence_level,
            "event_count": self.event_count,
            "interval_method_id": self.interval_method_id,
            "synthetic": self.synthetic,
            "effect_estimate": self.effect_estimate.to_dict() if self.effect_estimate else None,
        }


class ProtocolConflict(ValueError):
    pass


class MethodQualificationConflict(ValueError):
    pass


class CohortProtocolStore:
    """Durable first-slice protocol/cohort state."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def document(self) -> dict[str, Any]:
        return read_json(self.path, {}) or {}

    def cohorts(self) -> tuple[CohortRecord, ...]:
        payload = self.document()
        records: list[CohortRecord] = []
        for item in payload.get("cohorts", []):
            events = tuple(StructuralEvent(**event) for event in item.get("events", []))
            records.append(CohortRecord(
                cohort_id=item["cohort_id"],
                ordinal=int(item["ordinal"]),
                first_entry_session=item["first_entry_session"],
                last_entry_session=item["last_entry_session"],
                matured=bool(item["matured"]),
                protocol_hash=item["protocol_hash"],
                events=events,
                source_manifest_hash=item.get("source_manifest_hash", ""),
            ))
        return tuple(records)

    def register_cohort(
        self,
        config: ProtocolConfig,
        cohort: CohortRecord,
        calendar: SessionCalendar,
    ) -> CohortRecord:
        problems = list(config.violations())
        if cohort.protocol_hash != config.protocol_hash:
            problems.append(PROTOCOL_MISMATCH)
        payload = self.document()
        frozen = payload.get("protocol_hash")
        if frozen is not None and frozen != config.protocol_hash:
            problems.append(PROTOCOL_MISMATCH)

        normalized = cohort.to_dict()
        for existing in payload.get("cohorts", []):
            if existing.get("cohort_id") == cohort.cohort_id:
                if _sha256_document(existing) != _sha256_document(normalized):
                    raise ProtocolConflict("COHORT_ID_REUSED_WITH_DIFFERENT_PAYLOAD")
                if problems:
                    raise ProtocolConflict(";".join(sorted(set(problems))))
                return cohort

        current = list(self.cohorts())
        if current:
            if any(not item.matured for item in current):
                problems.append("PRIOR_COHORT_NOT_FULLY_MATURED")
            elif structural_stopping_decision(
                tuple(current), calendar, config
            ).inference_eligible:
                problems.append(COHORT_ACCRUAL_AFTER_STRUCTURAL_STOP)
        expected_ordinal = len(current) + 1
        if cohort.ordinal != expected_ordinal:
            problems.append(
                f"COHORT_ORDINAL_EXPECTED_{expected_ordinal}_GOT_{cohort.ordinal}"
            )
        if cohort.ordinal > config.k_max:
            problems.append(FIFTH_COHORT_REFUSED)
        problems.extend(cohort_geometry_violations(cohort, calendar, config))
        if current:
            previous = current[-1]
            if previous.protocol_hash != config.protocol_hash:
                problems.append(PROTOCOL_MISMATCH)
            gap = _session_gap_after(
                previous.last_entry_session, cohort.first_entry_session, calendar
            )
            if gap is None or gap < config.inter_cohort_separation:
                problems.append(COHORT_GAP_VIOLATION)
        if problems:
            raise ProtocolConflict(";".join(sorted(set(problems))))

        output = {
            "version": 1,
            "protocol_id": config.protocol_id,
            "protocol_hash": config.protocol_hash,
            "protocol_config": config.to_dict(),
            "cohorts": payload.get("cohorts", []) + [normalized],
        }
        write_json(self.path, output)
        return cohort


class MethodQualificationStore:
    """Durable, conflict-detecting qualification artifacts keyed by id."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def record(self, artifact: MethodQualificationArtifact) -> MethodQualificationArtifact:
        payload = read_json(self.path, {}) or {}
        items = dict(payload.get("artifacts", {}))
        document = artifact.to_dict()
        existing = items.get(artifact.qualification_id)
        if existing is not None:
            if _sha256_document(existing) != _sha256_document(document):
                raise MethodQualificationConflict(
                    "METHOD_QUALIFICATION_ID_REUSED_WITH_DIFFERENT_PAYLOAD"
                )
            return artifact
        items[artifact.qualification_id] = document
        write_json(self.path, {"version": 1, "artifacts": items})
        return artifact


def build_delta_coordinate_binding(
    *,
    benchmark_symbol: str = "SPY",
    security_terminal_treatment: str = TERMINAL_TREATMENT,
    benchmark_terminal_treatment: str = TERMINAL_TREATMENT,
    allocation_constructor_id: str = ALLOCATION_CONSTRUCTOR_ID,
    d19_reference: str | None = D19_REFERENCE,
) -> DeltaCoordinateBinding:
    return DeltaCoordinateBinding(
        security=ReturnConvention(
            return_definition=RETURN_DEFINITION,
            interval_spec=INTERVAL_SPEC,
            corporate_action_convention=CORPORATE_ACTION_CONVENTION,
            terminal_treatment=security_terminal_treatment,
        ),
        benchmark=ReturnConvention(
            return_definition=RETURN_DEFINITION,
            interval_spec=INTERVAL_SPEC,
            corporate_action_convention=CORPORATE_ACTION_CONVENTION,
            terminal_treatment=benchmark_terminal_treatment,
        ),
        benchmark_symbol=benchmark_symbol,
        aggregation=ALLOCATION_WEIGHTED_RATIO,
        allocation_constructor_id=allocation_constructor_id,
        allocation_weight_precedes_outcome=True,
        d19_reference=d19_reference,
    )


def _session_gap_after(
    previous_last: str, next_first: str, calendar: SessionCalendar
) -> int | None:
    left = calendar.index_of(previous_last)
    right = calendar.index_of(next_first)
    if left is None or right is None or right <= left:
        return None
    return right - left


def cohort_geometry_violations(
    cohort: CohortRecord,
    calendar: SessionCalendar,
    config: ProtocolConfig = ProtocolConfig(),
) -> tuple[str, ...]:
    problems: list[str] = []
    first = calendar.index_of(cohort.first_entry_session)
    last = calendar.index_of(cohort.last_entry_session)
    if first is None or last is None:
        problems.append("COHORT_BOUNDARY_OFF_CALENDAR")
        return tuple(problems)
    if last - first + 1 != config.entry_sessions_per_cohort:
        problems.append("COHORT_ENTRY_SESSION_GEOMETRY_NOT_252")
    for event in cohort.events:
        entry = calendar.index_of(event.entry_session)
        exit_position = calendar.index_of(event.scheduled_exit_session)
        if entry is None or exit_position is None:
            problems.append(f"EVENT_OFF_CALENDAR:{event.event_id}")
            continue
        if not first <= entry <= last:
            problems.append(f"EVENT_OUTSIDE_COHORT:{event.event_id}")
        if exit_position - entry != HOLDING_SESSIONS - 1:
            problems.append(f"SCHEDULED_EXIT_NOT_E_PLUS_19:{event.event_id}")
        if entry - INFLUENCE_LEAD_SESSIONS < 0:
            problems.append(f"INFLUENCE_WARMUP_UNAVAILABLE:{event.event_id}")
        if exit_position + INFLUENCE_POST_SESSIONS >= len(calendar):
            problems.append(f"INFLUENCE_POST_BUFFER_UNAVAILABLE:{event.event_id}")
        if not _finite_nonnegative(event.allocation_weight):
            problems.append(f"INVALID_ALLOCATION_WEIGHT:{event.event_id}")
        if not _finite(event.adv20_usd) or event.adv20_usd <= 0:
            problems.append(f"INVALID_ADV20:{event.event_id}")
        maximum = min(PER_SLOT_CAP, PARTICIPATION_CEILING * event.adv20_usd)
        if event.allocation_weight > maximum + 1e-12:
            problems.append(f"ALLOCATION_EXCEEDS_FROZEN_CONSTRUCTOR_CAP:{event.event_id}")
        if not event.allocation_commitment_hash:
            problems.append(f"ALLOCATION_COMMITMENT_MISSING:{event.event_id}")
    return tuple(sorted(set(problems)))


def commit_reference_allocations(
    candidates: Sequence[AllocationCandidate],
    calendar: SessionCalendar,
) -> tuple[StructuralEvent, ...]:
    """Apply the frozen 20-slot/ADV20 reference policy before target outcomes."""
    ordered: list[tuple[int, AllocationCandidate]] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate.event_id in seen:
            raise ValueError(f"DUPLICATE_EVENT_ID:{candidate.event_id}")
        seen.add(candidate.event_id)
        entry_index = calendar.index_of(candidate.entry_session)
        if entry_index is None:
            raise ValueError(f"ENTRY_SESSION_OFF_CALENDAR:{candidate.event_id}")
        if not _finite(candidate.adv20_usd) or candidate.adv20_usd <= 0:
            raise ValueError(f"INVALID_ADV20:{candidate.event_id}")
        ordered.append((entry_index, candidate))
    ordered.sort(key=lambda item: (
        item[0], item[1].issuer_cik, item[1].security_id,
        item[1].crossing_id, item[1].event_id,
    ))

    active: dict[int, tuple[str, int]] = {}
    events: list[StructuralEvent] = []
    for entry_index, candidate in ordered:
        for slot, (_issuer, exit_index) in list(active.items()):
            if exit_index < entry_index:
                del active[slot]
        issuer_active = any(
            issuer == candidate.issuer_cik for issuer, _exit in active.values()
        )
        exit_index = entry_index + HOLDING_SESSIONS - 1
        exit_session = calendar.at(exit_index)
        if exit_session is None:
            raise ValueError(f"SCHEDULED_EXIT_OFF_CALENDAR:{candidate.event_id}")

        if issuer_active:
            slot = None
            reason = "ISSUER_ALREADY_HAS_ACTIVE_SLOT"
            weight = 0.0
        elif len(active) >= SLOT_COUNT:
            slot = None
            reason = "ALL_REFERENCE_SLOTS_OCCUPIED"
            weight = 0.0
        else:
            slot = next(index for index in range(SLOT_COUNT) if index not in active)
            active[slot] = (candidate.issuer_cik, exit_index)
            reason = "POSITIVE_REFERENCE_ALLOCATION"
            weight = min(PER_SLOT_CAP, PARTICIPATION_CEILING * candidate.adv20_usd)

        commitment_document = {
            "rule_hash": ALLOCATION_RULE_HASH,
            "event_id": candidate.event_id,
            "issuer_cik": candidate.issuer_cik,
            "security_id": candidate.security_id,
            "crossing_id": candidate.crossing_id,
            "entry_session": candidate.entry_session,
            "scheduled_exit_session": exit_session,
            "adv20_usd": candidate.adv20_usd,
            "slot": slot,
            "allocation_weight": weight,
            "reason": reason,
            "content_addresses": sorted(candidate.content_addresses),
        }
        events.append(StructuralEvent(
            event_id=candidate.event_id,
            issuer_cik=candidate.issuer_cik,
            security_id=candidate.security_id,
            crossing_id=candidate.crossing_id,
            entry_session=candidate.entry_session,
            scheduled_exit_session=exit_session,
            allocation_weight=weight,
            adv20_usd=candidate.adv20_usd,
            allocation_slot=slot,
            allocation_reason=reason,
            allocation_commitment_hash=_sha256_document(commitment_document),
            content_addresses=tuple(sorted(candidate.content_addresses)),
        ))
    return tuple(events)


class _UnionFind:
    def __init__(self, keys: Iterable[str]):
        self.parent = {key: key for key in keys}

    def find(self, key: str) -> str:
        parent = self.parent[key]
        if parent != key:
            self.parent[key] = self.find(parent)
        return self.parent[key]

    def union(self, left: str, right: str) -> None:
        a, b = self.find(left), self.find(right)
        if a != b:
            winner, loser = sorted((a, b))
            self.parent[loser] = winner


def _component_id(members: Sequence[str]) -> str:
    return "component:" + hashlib.sha256(
        "|".join(sorted(members)).encode("utf-8")
    ).hexdigest()


def connected_components(
    cohorts: Sequence[CohortRecord],
    calendar: SessionCalendar,
    corporate_links: Mapping[str, str] | None = None,
) -> tuple[dict[str, str], dict[str, float]]:
    """Components over all accrued cohorts, issuer/corporate and time connected."""
    events = [event for cohort in cohorts for event in cohort.events]
    ids = [event.event_id for event in events]
    if len(set(ids)) != len(ids):
        raise ValueError("DUPLICATE_EVENT_ID_ACROSS_COHORTS")
    union = _UnionFind(ids)
    corporate_links = corporate_links or {}

    def identity(event: StructuralEvent) -> str:
        return (
            event.corporate_group
            or corporate_links.get(event.issuer_cik)
            or event.issuer_cik
        )

    spans: dict[str, tuple[int, int]] = {}
    for event in events:
        entry = calendar.index_of(event.entry_session)
        exit_position = calendar.index_of(event.scheduled_exit_session)
        if entry is None or exit_position is None:
            raise ValueError(f"EVENT_OFF_CALENDAR:{event.event_id}")
        spans[event.event_id] = (
            entry - INFLUENCE_LEAD_SESSIONS,
            exit_position + INFLUENCE_POST_SESSIONS,
        )

    for index, left in enumerate(events):
        for right in events[index + 1:]:
            issuer_link = identity(left) == identity(right)
            left_span, right_span = spans[left.event_id], spans[right.event_id]
            time_link = max(left_span[0], right_span[0]) <= min(
                left_span[1], right_span[1]
            )
            if issuer_link or time_link:
                union.union(left.event_id, right.event_id)

    grouped: dict[str, list[str]] = {}
    for event_id in ids:
        grouped.setdefault(union.find(event_id), []).append(event_id)
    canonical: dict[str, str] = {}
    for members in grouped.values():
        component = _component_id(members)
        for event_id in members:
            canonical[event_id] = component

    exposures: dict[str, float] = {}
    event_by_id = {event.event_id: event for event in events}
    for event_id, component in canonical.items():
        weight = event_by_id[event_id].allocation_weight
        if weight > 0:
            exposures[component] = exposures.get(component, 0.0) + weight
    return canonical, exposures


def structural_stopping_decision(
    cohorts: Sequence[CohortRecord],
    calendar: SessionCalendar,
    config: ProtocolConfig = ProtocolConfig(),
    corporate_links: Mapping[str, str] | None = None,
) -> StructuralStoppingDecision:
    """One-look firewall: this signature intentionally has no outcome input."""
    if config.violations():
        return StructuralStoppingDecision(
            STRUCTURAL_INSUFFICIENT, config.violations(), len(cohorts), 0, 0,
            0.0, None, (), (),
        )
    if len(cohorts) > config.k_max:
        return StructuralStoppingDecision(
            STRUCTURAL_INSUFFICIENT, (FIFTH_COHORT_REFUSED,), len(cohorts), 0, 0,
            0.0, None, (), (),
        )
    matured = [cohort for cohort in cohorts if cohort.matured]
    if len(matured) != len(cohorts):
        return StructuralStoppingDecision(
            STRUCTURAL_CONTINUE, ("COHORT_NOT_FULLY_MATURED",), len(cohorts),
            len(matured), 0, 0.0, None, (), (),
        )
    if not cohorts:
        return StructuralStoppingDecision(
            STRUCTURAL_CONTINUE, ("NO_COHORT_ACCRUED",), 0, 0, 0, 0.0, None, (), (),
        )

    for index, cohort in enumerate(cohorts):
        problems = cohort_geometry_violations(cohort, calendar, config)
        if problems:
            return StructuralStoppingDecision(
                STRUCTURAL_INSUFFICIENT, problems, len(cohorts), len(matured), 0,
                0.0, None, (), (),
            )
        if cohort.protocol_hash != config.protocol_hash:
            return StructuralStoppingDecision(
                STRUCTURAL_INSUFFICIENT, (PROTOCOL_MISMATCH,), len(cohorts),
                len(matured), 0, 0.0, None, (), (),
            )
        if index:
            gap = _session_gap_after(
                cohorts[index - 1].last_entry_session,
                cohort.first_entry_session,
                calendar,
            )
            if gap is None or gap < config.inter_cohort_separation:
                return StructuralStoppingDecision(
                    STRUCTURAL_INSUFFICIENT, (COHORT_GAP_VIOLATION,), len(cohorts),
                    len(matured), 0, 0.0, None, (), (),
                )

    assignments, exposures = connected_components(
        cohorts, calendar, corporate_links
    )
    positive = {key: value for key, value in exposures.items() if value > 0}
    total = float(sum(positive.values()))
    g = len(positive)
    share = max(positive.values()) / total if total > 0 and positive else None
    assignment_rows = tuple(sorted(assignments.items()))
    exposure_rows = tuple(sorted(positive.items()))

    reasons: list[str] = []
    if g < config.g_min:
        reasons.append(INSUFFICIENT_G)
    if share is not None and share > config.max_component_exposure_share + 1e-12:
        reasons.append(CONCENTRATION_GUARD_FAILED)

    if g >= config.g_min and share is not None and (
        share <= config.max_component_exposure_share + 1e-12
    ):
        state = STRUCTURAL_INFERENCE_ELIGIBLE
        reasons = []
    elif len(cohorts) >= config.k_max:
        state = STRUCTURAL_INSUFFICIENT
    else:
        state = STRUCTURAL_CONTINUE

    return StructuralStoppingDecision(
        state=state,
        reasons=tuple(sorted(set(reasons))),
        cohort_count=len(cohorts),
        matured_cohort_count=len(matured),
        positive_exposure_components=g,
        total_positive_exposure=total,
        max_component_exposure_share=share,
        component_assignments=assignment_rows,
        component_exposures=exposure_rows,
    )


def _quantile_bounds(
    sorted_values: Sequence[float],
    confidence_level: float,
) -> tuple[float, float]:
    tail = (1.0 - confidence_level) / 2.0
    count = len(sorted_values)
    lower_index = max(0, int(math.floor(tail * count)))
    upper_index = min(
        count - 1, int(math.ceil((1.0 - tail) * count)) - 1
    )
    return float(sorted_values[lower_index]), float(sorted_values[upper_index])


def sign_flip_interval(
    weights: Sequence[float],
    outcomes: Sequence[float],
    components: Sequence[Any],
    *,
    confidence_level: float = CONFIDENCE_LEVEL,
    seed: int = DEFAULT_SIGN_SEED,
    draws: int = DEFAULT_SIGN_DRAWS,
    exhaustive_component_limit: int = EXHAUSTIVE_COMPONENT_LIMIT,
) -> SignFlipInterval:
    """Whole-component Rademacher interval for the weighted-ratio score."""
    if len(weights) != len(outcomes) or len(weights) != len(components):
        raise ValueError("weights, outcomes and components must align")
    if not (0.0 < confidence_level < 1.0):
        raise ValueError("confidence_level must be in (0,1)")
    if any(not _finite_nonnegative(value) for value in weights):
        return SignFlipInterval(
            INVALID_SCIENTIFIC_INPUT, None, None, None, confidence_level,
            INTERVAL_METHOD_ID, 0, len(weights), float("nan"), "NONE", 0, None,
            "weights must be finite and nonnegative",
        )
    if any(not _finite(value) for value in outcomes):
        return SignFlipInterval(
            INVALID_SCIENTIFIC_INPUT, None, None, None, confidence_level,
            INTERVAL_METHOD_ID, 0, len(weights), float(sum(weights)), "NONE", 0, None,
            "outcomes must be finite",
        )
    denominator = float(sum(weights))
    if not _finite(denominator) or denominator <= 0:
        return SignFlipInterval(
            "NO_DEPLOYED_EXPOSURE", None, None, None, confidence_level,
            INTERVAL_METHOD_ID, 0, len(weights), denominator, "NONE", 0, None,
            "sum of allocation weights is not positive",
        )
    point = float(sum(w * y for w, y in zip(weights, outcomes))) / denominator
    grouped: dict[Any, list[int]] = {}
    for index, component in enumerate(components):
        grouped.setdefault(component, []).append(index)
    order = sorted(grouped, key=repr)
    g = len(order)
    if g < 2:
        return SignFlipInterval(
            "VARIANCE_UNIDENTIFIED_FROM_ONE_CLUSTER", point, None, None,
            confidence_level, INTERVAL_METHOD_ID, g, len(weights), denominator,
            "NONE", 0, None, "one component cannot identify interval variation",
        )

    contributions = [
        sum(weights[index] * (outcomes[index] - point)
            for index in grouped[key])
        for key in order
    ]

    samples: list[float] = []
    if g <= exhaustive_component_limit:
        for vector in itertools.product((-1.0, 1.0), repeat=g):
            samples.append(
                point + sum(sign * contribution
                            for sign, contribution in zip(vector, contributions))
                / denominator
            )
        enumeration = "EXHAUSTIVE_RADEMACHER"
        used_seed: int | None = None
    else:
        if draws < 2:
            raise ValueError("draws must be >=2 for sampled sign-flip")
        generator = random.Random(seed)
        for _ in range(draws):
            total = sum(
                (1.0 if generator.getrandbits(1) else -1.0) * contribution
                for contribution in contributions
            )
            samples.append(point + total / denominator)
        enumeration = "SEEDED_RADEMACHER_SAMPLE"
        used_seed = seed

    if not samples or any(not _finite(value) for value in samples):
        return SignFlipInterval(
            "INTERVAL_NONFINITE", point, None, None, confidence_level,
            INTERVAL_METHOD_ID, g, len(weights), denominator, enumeration,
            len(samples), used_seed, "nonfinite sign-flip sample",
        )
    samples.sort()
    lower, upper = _quantile_bounds(samples, confidence_level)
    if not (lower <= point <= upper):
        return SignFlipInterval(
            "POINT_OUTSIDE_INTERVAL", point, lower, upper, confidence_level,
            INTERVAL_METHOD_ID, g, len(weights), denominator, enumeration,
            len(samples), used_seed, "interval does not contain point estimate",
        )
    return SignFlipInterval(
        "ESTIMATE_RESOLVED", point, lower, upper, confidence_level,
        INTERVAL_METHOD_ID, g, len(weights), denominator, enumeration,
        len(samples), used_seed,
        "whole connected-component score sign flips; weighted-ratio denominator",
    )


def _qualification_fixture(
    name: str,
    weights: Sequence[float],
    outcomes: Sequence[float],
    components: Sequence[str],
) -> QualificationStressResult:
    interval = sign_flip_interval(weights, outcomes, components)
    passed = interval.resolved
    if name == "positive_effect" and interval.point is not None:
        passed = passed and interval.point > 0
    elif name == "null_effect" and interval.point is not None:
        passed = passed and abs(interval.point) < 1e-12
    elif name == "one_dominant_exposure_component":
        totals: dict[str, float] = {}
        for weight, component in zip(weights, components):
            totals[component] = totals.get(component, 0.0) + weight
        total = sum(totals.values())
        share = max(totals.values()) / total if total else 1.0
        passed = share > MAX_COMPONENT_EXPOSURE_SHARE
    elif name == "insufficient_component_count":
        passed = len(set(components)) < G_MIN
    detail = interval.state
    if name in {"one_dominant_exposure_component", "insufficient_component_count"}:
        detail = "guard condition detected"
    return QualificationStressResult(name, passed, detail)


def qualify_method(
    config: ProtocolConfig = ProtocolConfig(),
    *,
    runtime_identity: str = "PYTHON_STDLIB_RANDOM+ITERTOOLS_PRODUCT",
    target_cohort_applicability_supported: bool = False,
    applicability_evidence_hash: str | None = None,
    applicability_statement: str = (
        "Synthetic qualification establishes numerical behavior only; "
        "target-cohort dependence applicability requires separate evidence."
    ),
) -> MethodQualificationArtifact:
    """Run the target-outcome-independent deterministic ten-case stress matrix."""
    base_components = [f"c{i}" for i in range(10)]
    equal = [1.0] * 10
    tests = [
        _qualification_fixture(
            "null_effect", equal,
            [-0.02, 0.02, -0.01, 0.01, -0.03, 0.03, -0.015, 0.015, -0.005, 0.005],
            base_components,
        ),
        _qualification_fixture(
            "positive_effect", equal,
            [0.01, 0.02, 0.015, 0.03, 0.025, 0.01, 0.02, 0.015, 0.03, 0.025],
            base_components,
        ),
        _qualification_fixture(
            "common_market_shock", equal,
            [0.02 + (0.004 if i % 2 else -0.004) for i in range(10)],
            base_components,
        ),
        _qualification_fixture(
            "repeated_issuer_dependence", equal,
            [0.02 + i * 0.001 for i in range(10)],
            ["issuer-a", "issuer-a"] + [f"c{i}" for i in range(2, 10)],
        ),
        _qualification_fixture(
            "overlapping_influence_windows", equal,
            [0.01 + i * 0.001 for i in range(10)],
            ["overlap-a", "overlap-a", "overlap-b", "overlap-b"]
            + [f"c{i}" for i in range(4, 10)],
        ),
        _qualification_fixture(
            "unequal_allocations",
            [1.0, 1.2, 0.7, 1.1, 0.9, 1.3, 0.8, 1.05, 0.95, 1.0],
            [0.01 + i * 0.001 for i in range(10)], base_components,
        ),
        _qualification_fixture(
            "random_denominator",
            [0.4, 1.8, 0.7, 2.0, 0.6, 1.3, 0.9, 1.1, 0.5, 1.6],
            [0.01 + i * 0.002 for i in range(10)], base_components,
        ),
        _qualification_fixture(
            "one_dominant_exposure_component",
            [20.0] + [1.0] * 9, [0.01] * 10, base_components,
        ),
        _qualification_fixture(
            "insufficient_component_count",
            [1.0] * 8, [0.01] * 8, [f"c{i}" for i in range(8)],
        ),
        QualificationStressResult(
            "dependence_model_misspecification_stress",
            True,
            "unsupported cross-component dependence is explicitly not certified "
            "by synthetic numerical qualification",
        ),
    ]
    numerical = all(item.passed for item in tests)
    fixture_identity = _sha256_document([asdict(item) for item in tests])
    qualification_id = _sha256_document({
        "protocol_hash": config.protocol_hash,
        "method_id": INTERVAL_METHOD_ID,
        "version": QUALIFICATION_VERSION,
        "runtime_identity": runtime_identity,
        "fixture_identity": fixture_identity,
        "target_cohort_applicability_supported": target_cohort_applicability_supported,
        "applicability_evidence_hash": applicability_evidence_hash,
    })
    return MethodQualificationArtifact(
        qualification_id=qualification_id,
        protocol_id=config.protocol_id,
        protocol_hash=config.protocol_hash,
        method_id=INTERVAL_METHOD_ID,
        method_version=QUALIFICATION_VERSION,
        algorithm_id=INTERVAL_ALGORITHM_ID,
        runtime_identity=runtime_identity,
        confidence_level=CONFIDENCE_LEVEL,
        random_denominator_treatment="RATIO_SCORE_SUM_AJ_TIMES_TJ_MINUS_DELTA_OVER_SUM_AJ",
        component_definition=(
            "UNION_OF_ACCRUED_COHORTS_CONNECTED_BY_INFLUENCE_SPAN_OR_"
            "ISSUER_CORPORATE_RECURRENCE"
        ),
        enumeration_rule=(
            f"EXHAUSTIVE_2^G_FOR_G_LE_{EXHAUSTIVE_COMPONENT_LIMIT};"
            f"ELSE_SEEDED_{DEFAULT_SIGN_DRAWS}_DRAWS_SEED_{DEFAULT_SIGN_SEED}"
        ),
        declared_dependence_assumptions=(
            "DEPENDENCE_IS_CONTAINED_WITHIN_DECLARED_CONNECTED_COMPONENTS",
            "CROSS_COMPONENT_SCORE_SIGNS_ARE_EXCHANGEABLE_UNDER_NULL",
            "FINITE_SECOND_MOMENTS",
            "NO_DOMINANT_COMPONENT_AFTER_0_10_GUARD",
        ),
        concentration_guard="MAX_COMPONENT_EXPOSURE_SHARE_LE_0_10",
        fixture_identity=fixture_identity,
        stress_results=tuple(tests),
        numerical_qualification_passed=numerical,
        target_cohort_applicability_supported=target_cohort_applicability_supported,
        applicability_evidence_hash=applicability_evidence_hash,
        applicability_statement=applicability_statement,
        limitations=(
            "SYNTHETIC_STRESS_DOES_NOT_PROVE_REAL_FORM4_ALPHA",
            "SYNTHETIC_STRESS_DOES_NOT_PROVE_REAL_WORLD_INDEPENDENCE",
            "SYNTHETIC_STRESS_DOES_NOT_PROVE_CALIBRATED_PROFITABILITY",
            "SYNTHETIC_STRESS_DOES_NOT_PROVE_REAL_DATA_AVAILABILITY",
        ),
        synthetic_only=True,
    )


def _sample_id(
    config: ProtocolConfig,
    cohorts: Sequence[CohortRecord],
    decision: StructuralStoppingDecision,
) -> str:
    return _sha256_document({
        "protocol_hash": config.protocol_hash,
        "cohorts": [
            {
                "cohort_id": cohort.cohort_id,
                "source_manifest_hash": cohort.source_manifest_hash,
                "event_ids": [event.event_id for event in cohort.events],
                "allocation_commitments": [
                    event.allocation_commitment_hash for event in cohort.events
                ],
            }
            for cohort in cohorts
        ],
        "components": list(decision.component_assignments),
    })


def _refusal(
    *,
    config: ProtocolConfig,
    cohorts: Sequence[CohortRecord],
    decision: StructuralStoppingDecision,
    reasons: Sequence[str],
    sample_id: str,
    d19_complete: bool,
    qualification: MethodQualificationArtifact | None = None,
    binding: DeltaCoordinateBinding | None = None,
    binding_hash: str | None = None,
    synthetic: bool = False,
) -> ScientificEffectArtifact:
    provenance = _sha256_document({
        "protocol_hash": config.protocol_hash,
        "sample_id": sample_id,
        "status": "REFUSED",
        "reasons": sorted(set(reasons)),
    })
    qualification_hash = _sha256_document(qualification.to_dict()) if qualification else None
    return ScientificEffectArtifact(
        status="REFUSED",
        reason_codes=tuple(sorted(set(reasons))),
        protocol_id=config.protocol_id,
        protocol_hash=config.protocol_hash,
        sample_id=sample_id,
        cohort_ids=tuple(cohort.cohort_id for cohort in cohorts),
        sample_provenance=provenance,
        allocation_constructor_id=config.allocation_constructor_id,
        allocation_commitment_hashes=tuple(sorted(
            event.allocation_commitment_hash
            for cohort in cohorts for event in cohort.events
        )),
        component_assignments=decision.component_assignments,
        d19_complete=d19_complete,
        method_qualification_id=qualification.qualification_id if qualification else None,
        method_qualification_hash=qualification_hash,
        delta_coordinate_binding=binding,
        delta_coordinate_hash=binding_hash,
        evidence_label=EVIDENCE_DEVELOPMENT,
        point=None,
        lower=None,
        upper=None,
        confidence_level=CONFIDENCE_LEVEL,
        event_count=0,
        interval_method_id=None,
        synthetic=synthetic,
        effect_estimate=None,
    )


def assemble_form4_effect(
    *,
    cohorts: Sequence[CohortRecord],
    calendar: SessionCalendar,
    outcomes: Mapping[str, float],
    method_qualification: MethodQualificationArtifact | None,
    forward_receipt: ForwardConfirmationReceipt | None = None,
    config: ProtocolConfig = ProtocolConfig(),
    corporate_links: Mapping[str, str] | None = None,
    binding: DeltaCoordinateBinding | None = None,
    synthetic: bool = False,
) -> ScientificEffectArtifact:
    """Assemble the frozen effect or refuse, preserving the one-look ordering."""
    decision = structural_stopping_decision(
        cohorts, calendar, config, corporate_links
    )
    sample_id = _sample_id(config, cohorts, decision)

    if decision.state == STRUCTURAL_CONTINUE:
        return _refusal(
            config=config, cohorts=cohorts, decision=decision,
            reasons=decision.reasons or ("STRUCTURAL_GUARD_NOT_YET_REACHED",),
            sample_id=sample_id,
            d19_complete=all(
                event.d19_complete for cohort in cohorts for event in cohort.events
            ),
            synthetic=synthetic,
        )
    if decision.state == STRUCTURAL_INSUFFICIENT:
        return _refusal(
            config=config, cohorts=cohorts, decision=decision,
            reasons=(STRUCTURAL_INSUFFICIENT,) + decision.reasons,
            sample_id=sample_id,
            d19_complete=all(
                event.d19_complete for cohort in cohorts for event in cohort.events
            ),
            synthetic=synthetic,
        )

    positive_events = [
        event for cohort in cohorts for event in cohort.events
        if event.allocation_weight > 0
    ]
    d19_complete = all(event.d19_complete for event in positive_events)
    if not d19_complete:
        return _refusal(
            config=config, cohorts=cohorts, decision=decision,
            reasons=(D19_INSUFFICIENT, EFFECT_UNAVAILABLE),
            sample_id=sample_id, d19_complete=False, synthetic=synthetic,
        )

    if (
        method_qualification is None
        or method_qualification.protocol_hash != config.protocol_hash
        or method_qualification.method_id != config.interval_method_id
        or not method_qualification.numerical_qualification_passed
    ):
        return _refusal(
            config=config, cohorts=cohorts, decision=decision,
            reasons=(DEPENDENCE_MODEL_UNSUPPORTED, EFFECT_UNAVAILABLE),
            sample_id=sample_id, d19_complete=True,
            qualification=method_qualification, synthetic=synthetic,
        )

    binding = binding or build_delta_coordinate_binding(
        allocation_constructor_id=config.allocation_constructor_id
    )
    coordinate = evaluate_delta_coordinate(binding)
    if coordinate.state == DELTA_COORDINATE_UNRESOLVED:
        return _refusal(
            config=config, cohorts=cohorts, decision=decision,
            reasons=(DELTA_COORDINATE_UNRESOLVED, EFFECT_UNAVAILABLE) + coordinate.reasons,
            sample_id=sample_id, d19_complete=True,
            qualification=method_qualification, binding=binding,
            synthetic=synthetic,
        )
    if coordinate.state == DELTA_COORDINATE_MISMATCH:
        return _refusal(
            config=config, cohorts=cohorts, decision=decision,
            reasons=(DELTA_COORDINATE_MISMATCH, EFFECT_UNAVAILABLE) + coordinate.reasons,
            sample_id=sample_id, d19_complete=True,
            qualification=method_qualification, binding=binding,
            synthetic=synthetic,
        )
    if (
        binding.security.terminal_treatment != binding.benchmark.terminal_treatment
        or binding.security.terminal_treatment != TERMINAL_TREATMENT
    ):
        return _refusal(
            config=config, cohorts=cohorts, decision=decision,
            reasons=(DELTA_COORDINATE_MISMATCH,
                     "TERMINAL_TREATMENT_LINEAGE_MISMATCH", EFFECT_UNAVAILABLE),
            sample_id=sample_id, d19_complete=True,
            qualification=method_qualification, binding=binding,
            binding_hash=coordinate.binding_hash, synthetic=synthetic,
        )

    weights: list[float] = []
    values: list[float] = []
    components: list[str] = []
    assignment = dict(decision.component_assignments)
    missing: list[str] = []
    for event in positive_events:
        if event.event_id not in outcomes:
            missing.append(event.event_id)
            continue
        value = float(outcomes[event.event_id])
        if not _finite(value):
            missing.append(event.event_id)
            continue
        weights.append(float(event.allocation_weight))
        values.append(value)
        components.append(assignment[event.event_id])
    if missing:
        return _refusal(
            config=config, cohorts=cohorts, decision=decision,
            reasons=(D19_INSUFFICIENT, "MANDATORY_OUTCOME_MISSING_OR_NONFINITE",
                     EFFECT_UNAVAILABLE),
            sample_id=sample_id, d19_complete=False,
            qualification=method_qualification, binding=binding,
            binding_hash=coordinate.binding_hash, synthetic=synthetic,
        )

    diagnostic = ratio_estimate(
        weights, values, components, confidence_level=CONFIDENCE_LEVEL
    )
    interval = sign_flip_interval(
        weights, values, components, confidence_level=CONFIDENCE_LEVEL
    )
    if (
        diagnostic.point is None
        or not interval.resolved
        or interval.point is None
        or abs(diagnostic.point - interval.point) > 1e-12
    ):
        detail = "INTERVAL_NOT_RESOLVED"
        if (
            diagnostic.point is not None and interval.point is not None
            and abs(diagnostic.point - interval.point) > 1e-12
        ):
            detail = "RATIO_POINT_CROSSCHECK_FAILED"
        return _refusal(
            config=config, cohorts=cohorts, decision=decision,
            reasons=(EFFECT_UNAVAILABLE, interval.state, detail),
            sample_id=sample_id, d19_complete=True,
            qualification=method_qualification, binding=binding,
            binding_hash=coordinate.binding_hash, synthetic=synthetic,
        )

    qualification_hash = _sha256_document(method_qualification.to_dict())
    forward_ok = (
        not synthetic
        and method_qualification.qualified_for_forward_confirmation
        and forward_receipt is not None
        and forward_receipt.valid_for(config.protocol_hash, sample_id)
    )
    evidence_label = EVIDENCE_FORWARD_CONFIRMATION if forward_ok else EVIDENCE_DEVELOPMENT
    reasons: list[str] = []
    if not method_qualification.qualified_for_forward_confirmation:
        reasons.append(DEPENDENCE_MODEL_UNSUPPORTED)
    if synthetic:
        reasons.append("SYNTHETIC_FIXTURE_DEVELOPMENT_ONLY")
    if forward_receipt is None:
        reasons.append("FORWARD_CONFIRMATION_RECEIPT_MISSING")
    elif not forward_receipt.valid_for(config.protocol_hash, sample_id):
        reasons.append("FORWARD_CONFIRMATION_RECEIPT_INVALID")

    provenance_document = {
        "protocol_hash": config.protocol_hash,
        "sample_id": sample_id,
        "cohort_ids": [cohort.cohort_id for cohort in cohorts],
        "row_digest": _sha256_document([
            {
                "event_id": event.event_id,
                "weight": event.allocation_weight,
                "outcome": outcomes[event.event_id],
                "component": assignment[event.event_id],
            }
            for event in positive_events
        ]),
        "qualification_hash": qualification_hash,
        "coordinate_hash": coordinate.binding_hash,
        "interval": interval.to_dict(),
        "evidence_label": evidence_label,
        "synthetic": synthetic,
    }
    sample_provenance = _sha256_document(provenance_document)
    estimate = EffectEstimate(
        delta_hat=float(interval.point),
        lower=float(interval.lower),
        upper=float(interval.upper),
        confidence_level=CONFIDENCE_LEVEL,
        evidence_label=evidence_label,
        sample_provenance=sample_provenance,
        estimator_form=ALLOCATION_WEIGHTED_RATIO,
        event_count=len(positive_events),
        p_value=None,
        clustering_unit_provenance=CLUSTERING_UNIT_O4_RESOLVED,
    )
    violations = estimate.violations()
    if violations:
        return _refusal(
            config=config, cohorts=cohorts, decision=decision,
            reasons=(EFFECT_UNAVAILABLE,) + tuple(violations),
            sample_id=sample_id, d19_complete=True,
            qualification=method_qualification, binding=binding,
            binding_hash=coordinate.binding_hash, synthetic=synthetic,
        )

    return ScientificEffectArtifact(
        status="ESTIMATE_RESOLVED",
        reason_codes=tuple(sorted(set(reasons))),
        protocol_id=config.protocol_id,
        protocol_hash=config.protocol_hash,
        sample_id=sample_id,
        cohort_ids=tuple(cohort.cohort_id for cohort in cohorts),
        sample_provenance=sample_provenance,
        allocation_constructor_id=config.allocation_constructor_id,
        allocation_commitment_hashes=tuple(sorted(
            event.allocation_commitment_hash for event in positive_events
        )),
        component_assignments=decision.component_assignments,
        d19_complete=True,
        method_qualification_id=method_qualification.qualification_id,
        method_qualification_hash=qualification_hash,
        delta_coordinate_binding=binding,
        delta_coordinate_hash=coordinate.binding_hash,
        evidence_label=evidence_label,
        point=float(interval.point),
        lower=float(interval.lower),
        upper=float(interval.upper),
        confidence_level=CONFIDENCE_LEVEL,
        event_count=len(positive_events),
        interval_method_id=INTERVAL_METHOD_ID,
        synthetic=synthetic,
        effect_estimate=estimate,
    )


def one_look_signature_proof() -> bool:
    """Mechanical proof that structural stopping has no outcome-bearing input."""
    forbidden = {"outcomes", "target_outcomes", "t_j", "returns", "effects"}
    names = {
        name.lower()
        for name in inspect.signature(structural_stopping_decision).parameters
    }
    return names.isdisjoint(forbidden)
