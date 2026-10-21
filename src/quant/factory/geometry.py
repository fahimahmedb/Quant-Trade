"""Planned sample geometry for frozen experiments.

The historical Factory computed geometry from realized return vectors.  That
surface is intentionally superseded here: while outcomes are sealed, geometry is
only a preregistered declaration about the planned sample/dependence structure.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from math import isfinite
from typing import Any, Mapping
import hashlib
import json


class GeometryDeclarationError(ValueError):
    pass


class GeometryStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    DECLARED = "DECLARED"


def _hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class GeometryDeclaration:
    protocol_hash: str
    status: GeometryStatus = GeometryStatus.UNKNOWN
    observation_unit: str | None = None
    target_observations: int | None = None
    dependence_assumption: str | None = None
    cluster_key: str | None = None
    max_cluster_share: float | None = None
    sampling_rule: str | None = None
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.protocol_hash, str) or not self.protocol_hash.strip():
            raise GeometryDeclarationError("protocol_hash is required")
        if not isinstance(self.status, GeometryStatus):
            try:
                object.__setattr__(self, "status", GeometryStatus(self.status))
            except (TypeError, ValueError) as exc:
                raise GeometryDeclarationError("invalid geometry status") from exc
        if any(not isinstance(item, str) or not item.strip() for item in self.assumptions):
            raise GeometryDeclarationError("assumptions must be non-empty strings")
        if self.status is GeometryStatus.UNKNOWN:
            claimed = (
                self.observation_unit, self.target_observations, self.dependence_assumption,
                self.cluster_key, self.max_cluster_share, self.sampling_rule,
            )
            if any(item is not None for item in claimed):
                raise GeometryDeclarationError("UNKNOWN geometry cannot carry planned geometry claims")
            return
        if not isinstance(self.observation_unit, str) or not self.observation_unit.strip():
            raise GeometryDeclarationError("DECLARED geometry requires observation_unit")
        if isinstance(self.target_observations, bool) or not isinstance(self.target_observations, int) or self.target_observations <= 0:
            raise GeometryDeclarationError("target_observations must be a positive integer")
        if not isinstance(self.dependence_assumption, str) or not self.dependence_assumption.strip():
            raise GeometryDeclarationError("dependence_assumption is required")
        if not isinstance(self.sampling_rule, str) or not self.sampling_rule.strip():
            raise GeometryDeclarationError("sampling_rule is required")
        if self.cluster_key is not None and (not isinstance(self.cluster_key, str) or not self.cluster_key.strip()):
            raise GeometryDeclarationError("cluster_key must be null or a non-empty string")
        if self.max_cluster_share is not None:
            if isinstance(self.max_cluster_share, bool) or type(self.max_cluster_share) not in (int, float):
                raise GeometryDeclarationError("max_cluster_share must be numeric")
            share = float(self.max_cluster_share)
            if not isfinite(share) or not 0.0 < share <= 1.0:
                raise GeometryDeclarationError("max_cluster_share must be finite in (0, 1]")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["assumptions"] = list(self.assumptions)
        return payload

    @property
    def declaration_hash(self) -> str:
        return _hash(self.to_dict())


def unknown_geometry(protocol_hash: str, *, assumptions: tuple[str, ...] = ()) -> GeometryDeclaration:
    return GeometryDeclaration(protocol_hash=protocol_hash, assumptions=assumptions)


def geometry_from_mapping(protocol_hash: str, payload: Mapping[str, Any] | None) -> GeometryDeclaration:
    if payload is None:
        return unknown_geometry(protocol_hash)
    if not isinstance(payload, Mapping):
        raise GeometryDeclarationError("geometry declaration must be a mapping")
    allowed = {
        "status", "observation_unit", "target_observations", "dependence_assumption",
        "cluster_key", "max_cluster_share", "sampling_rule", "assumptions",
    }
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise GeometryDeclarationError("unexpected geometry fields: " + ",".join(unknown))
    return GeometryDeclaration(
        protocol_hash=protocol_hash,
        status=GeometryStatus(payload.get("status", "UNKNOWN")),
        observation_unit=payload.get("observation_unit"),
        target_observations=payload.get("target_observations"),
        dependence_assumption=payload.get("dependence_assumption"),
        cluster_key=payload.get("cluster_key"),
        max_cluster_share=payload.get("max_cluster_share"),
        sampling_rule=payload.get("sampling_rule"),
        assumptions=tuple(payload.get("assumptions") or ()),
    )
