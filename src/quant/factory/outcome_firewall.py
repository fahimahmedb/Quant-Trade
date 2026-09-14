"""Fail-closed outcome access control for preregistered Research Factory experiments."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Iterable, Mapping

from .experiments import BlueTeamGate, DatasetRef, ExperimentRecord, ExperimentStatus


class OutcomeFirewallError(PermissionError):
    pass


class ColumnRole(str, Enum):
    IDENTIFIER = "IDENTIFIER"
    FORMATION = "FORMATION"
    METADATA = "METADATA"
    OUTCOME = "OUTCOME"
    DERIVED = "DERIVED"


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    role: ColumnRole
    sources: tuple[str, ...] = ()
    alias_of: str | None = None


@dataclass(frozen=True)
class DataAccessRequest:
    dataset_ref: DatasetRef
    path: str
    columns: tuple[ColumnSpec, ...]
    operation: str = "load"


_OUTCOME_TOKENS = frozenset({
    "outcome", "outcomes", "return", "returns", "future", "forward", "pnl", "profit",
    "loss", "alpha", "excess", "label", "target", "response", "entryprice", "exitprice",
    "openprice", "closeprice", "price", "nav", "benchmarkreturn", "abnormalreturn",
})
_GENERIC_EVENT_ROLES: Mapping[str, ColumnRole] = {
    "event_id": ColumnRole.IDENTIFIER,
    "issuer_id": ColumnRole.IDENTIFIER,
    "event_time": ColumnRole.FORMATION,
    "formation_date": ColumnRole.FORMATION,
    "provenance": ColumnRole.METADATA,
    "status": ColumnRole.METADATA,
}
_SAFE_GEOMETRY_DERIVED = frozenset({
    "n", "annual_distribution", "events_per_issuer", "hhi", "effective_issuers",
    "overlapping_pairs", "events_with_any_overlap", "max_concurrent_windows",
    "cluster_count", "multi_event_cluster_count", "cluster_size_distribution", "max_cluster_size",
})


def _tokens(name: str) -> set[str]:
    compact = re.sub(r"[^a-z0-9]+", "", name.lower())
    split = set(re.findall(r"[a-z]+|[0-9]+", name.lower()))
    split.add(compact)
    return split


class OutcomeFirewall:
    """Blocks outcome loading/derivation unless an exact Blue Team capability is present.

    Security does not rely on the filesystem path. Known outcome content hashes are denied even
    when copied to another path, while column role, lexical checks and recursive lineage catch
    direct, aliased and derived outcome fields. Before Blue Team freeze, the only loadable raw
    fields are the six fields of the generic event contract; unknown opaque fields fail closed.
    """

    def __init__(self, known_outcome_hashes: Iterable[str] = ()) -> None:
        self._known_outcome_hashes = frozenset(known_outcome_hashes)

    def authorize(self, request: DataAccessRequest, experiment: ExperimentRecord,
                  gate: BlueTeamGate | None = None) -> None:
        outcome_tainted = self._request_is_outcome_tainted(request)
        if outcome_tainted:
            self._require_gate(experiment, gate)
            return
        try:
            self._require_pre_outcome_contract(request)
            return
        except OutcomeFirewallError:
            # Any opaque/non-generic field is treated as potentially outcome-bearing.
            # It becomes accessible only with the exact Blue Team capability, even if
            # the experiment object already says BLUE_FROZEN or TESTING.
            self._require_gate(experiment, gate)

    def _request_is_outcome_tainted(self, request: DataAccessRequest) -> bool:
        if request.dataset_ref.role in {"outcome", "benchmark"}:
            return True
        if request.dataset_ref.content_hash in self._known_outcome_hashes:
            return True
        if not request.columns:
            raise OutcomeFirewallError("column manifest is required; access fails closed")

        manifest: Mapping[str, ColumnSpec] = {column.name: column for column in request.columns}
        if len(manifest) != len(request.columns):
            raise OutcomeFirewallError("duplicate column names in manifest")

        memo: dict[str, bool] = {}
        visiting: set[str] = set()

        def tainted(name: str) -> bool:
            if name in memo:
                return memo[name]
            if name in visiting:
                raise OutcomeFirewallError("cyclic column lineage")
            spec = manifest.get(name)
            if spec is None:
                raise OutcomeFirewallError(f"unresolved lineage source: {name}")
            visiting.add(name)
            lexical = bool(_tokens(spec.name) & _OUTCOME_TOKENS)
            direct = spec.role == ColumnRole.OUTCOME
            alias = False
            if spec.alias_of is not None:
                if spec.alias_of not in manifest:
                    raise OutcomeFirewallError(f"unresolved alias source: {spec.alias_of}")
                alias = tainted(spec.alias_of)
            derived = False
            if spec.role == ColumnRole.DERIVED:
                if not spec.sources:
                    raise OutcomeFirewallError("derived columns require explicit lineage")
                derived = any(tainted(source) for source in spec.sources)
            elif spec.sources:
                raise OutcomeFirewallError("only DERIVED columns may declare sources")
            visiting.remove(name)
            memo[name] = lexical or direct or alias or derived
            return memo[name]

        return any(tainted(column.name) for column in request.columns)

    @staticmethod
    def _require_pre_outcome_contract(request: DataAccessRequest) -> None:
        manifest = {column.name: column for column in request.columns}
        for spec in request.columns:
            if spec.alias_of is not None:
                raise OutcomeFirewallError("aliases are not permitted before BLUE_FROZEN")
            if spec.role == ColumnRole.DERIVED:
                if spec.name not in _SAFE_GEOMETRY_DERIVED:
                    raise OutcomeFirewallError(
                        f"pre-outcome derivation {spec.name!r} is outside the geometry allowlist"
                    )
                if not spec.sources:
                    raise OutcomeFirewallError("pre-outcome geometry derivations require explicit lineage")
                for source in spec.sources:
                    source_spec = manifest.get(source)
                    expected_role = _GENERIC_EVENT_ROLES.get(source)
                    if source_spec is None or expected_role is None or source_spec.role != expected_role:
                        raise OutcomeFirewallError(
                            f"pre-outcome derivation source {source!r} is outside the generic event contract"
                        )
                continue
            expected_role = _GENERIC_EVENT_ROLES.get(spec.name)
            if expected_role is None:
                raise OutcomeFirewallError(
                    f"pre-outcome field {spec.name!r} is outside the generic event contract"
                )
            if spec.role != expected_role:
                raise OutcomeFirewallError(
                    f"pre-outcome field {spec.name!r} has role {spec.role.value}, expected {expected_role.value}"
                )

    @staticmethod
    def _require_gate(experiment: ExperimentRecord, gate: BlueTeamGate | None) -> None:
        post_freeze = {
            ExperimentStatus.BLUE_FROZEN,
            ExperimentStatus.TESTING,
            ExperimentStatus.PROMISING,
            ExperimentStatus.REJECT,
            ExperimentStatus.INSUFFICIENT,
            ExperimentStatus.RETIRED,
        }
        if experiment.status not in post_freeze:
            raise OutcomeFirewallError("outcomes are blocked before BLUE_FROZEN")
        if gate is None:
            raise OutcomeFirewallError("Blue Team gate required")
        if gate.authority != "BLUE_TEAM":
            raise OutcomeFirewallError("invalid gate authority")
        if gate.experiment_id != experiment.experiment_id or gate.version != experiment.version:
            raise OutcomeFirewallError("gate is bound to a different experiment/version")
        if gate.protocol_hash != experiment.protocol_hash:
            raise OutcomeFirewallError("protocol hash mismatch")
        payload = [ref.to_dict() for ref in experiment.dataset_refs]
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        dataset_set_hash = hashlib.sha256(encoded).hexdigest()
        if gate.dataset_set_hash != dataset_set_hash:
            raise OutcomeFirewallError("frozen dataset set mismatch")
