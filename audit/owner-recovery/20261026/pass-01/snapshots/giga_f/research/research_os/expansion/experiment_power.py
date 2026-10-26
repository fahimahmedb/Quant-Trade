"""Canonical pre-outcome power declarations for the Research Core.

No empirical effect, volatility, MDE, or sample size is invented here. UNKNOWN is
first-class. A normal-approximation calculation is available only when every
assumption is explicitly supplied by the frozen protocol owner.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from math import ceil, isfinite
from statistics import NormalDist
from typing import Any, Mapping
import hashlib
import json


class PowerDeclarationError(ValueError):
    pass


class PowerStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    DECLARED = "DECLARED"
    DERIVED_FROM_DECLARED_ASSUMPTIONS = "DERIVED_FROM_DECLARED_ASSUMPTIONS"


def _hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _finite_number(name: str, value: Any, *, lower: float | None = None, upper: float | None = None,
                   strict_lower: bool = False, strict_upper: bool = False) -> float:
    if isinstance(value, bool) or type(value) not in (int, float) or not isfinite(float(value)):
        raise PowerDeclarationError(f"{name} must be a finite non-bool number")
    number = float(value)
    if lower is not None and (number <= lower if strict_lower else number < lower):
        op = ">" if strict_lower else ">="
        raise PowerDeclarationError(f"{name} must be {op} {lower}")
    if upper is not None and (number >= upper if strict_upper else number > upper):
        op = "<" if strict_upper else "<="
        raise PowerDeclarationError(f"{name} must be {op} {upper}")
    return number


@dataclass(frozen=True)
class PowerDeclaration:
    protocol_hash: str
    status: PowerStatus = PowerStatus.UNKNOWN
    minimum_detectable_effect: float | None = None
    baseline_scale: float | None = None
    significance_level: float | None = None
    desired_power: float | None = None
    required_observations: int | None = None
    method: str | None = None
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.protocol_hash, str) or not self.protocol_hash.strip():
            raise PowerDeclarationError("protocol_hash is required")
        if not isinstance(self.status, PowerStatus):
            try:
                object.__setattr__(self, "status", PowerStatus(self.status))
            except (TypeError, ValueError) as exc:
                raise PowerDeclarationError("invalid power status") from exc
        if any(not isinstance(item, str) or not item.strip() for item in self.assumptions):
            raise PowerDeclarationError("assumptions must be non-empty strings")
        numeric = (
            self.minimum_detectable_effect, self.baseline_scale, self.significance_level,
            self.desired_power, self.required_observations,
        )
        if self.status is PowerStatus.UNKNOWN:
            if any(item is not None for item in numeric) or self.method not in (None, ""):
                raise PowerDeclarationError("UNKNOWN power cannot carry numeric or method claims")
            return
        _finite_number("minimum_detectable_effect", self.minimum_detectable_effect, lower=0.0, strict_lower=True)
        _finite_number("baseline_scale", self.baseline_scale, lower=0.0, strict_lower=True)
        _finite_number("significance_level", self.significance_level, lower=0.0, upper=1.0,
                       strict_lower=True, strict_upper=True)
        _finite_number("desired_power", self.desired_power, lower=0.5, upper=1.0,
                       strict_lower=True, strict_upper=True)
        if isinstance(self.required_observations, bool) or not isinstance(self.required_observations, int) or self.required_observations < 2:
            raise PowerDeclarationError("required_observations must be an integer >= 2")
        if not isinstance(self.method, str) or not self.method.strip():
            raise PowerDeclarationError("known power requires an explicit method")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["assumptions"] = list(self.assumptions)
        return payload

    @property
    def declaration_hash(self) -> str:
        return _hash(self.to_dict())


def unknown_power(protocol_hash: str, *, assumptions: tuple[str, ...] = ()) -> PowerDeclaration:
    return PowerDeclaration(protocol_hash=protocol_hash, assumptions=assumptions)


def derive_normal_approximation(
    *, protocol_hash: str, minimum_detectable_effect: float, baseline_scale: float,
    significance_level: float, desired_power: float, assumptions: tuple[str, ...],
) -> PowerDeclaration:
    """Derive n only from declared assumptions; this is not empirical evidence."""
    mde = _finite_number("minimum_detectable_effect", minimum_detectable_effect, lower=0.0, strict_lower=True)
    scale = _finite_number("baseline_scale", baseline_scale, lower=0.0, strict_lower=True)
    alpha = _finite_number("significance_level", significance_level, lower=0.0, upper=1.0,
                           strict_lower=True, strict_upper=True)
    power = _finite_number("desired_power", desired_power, lower=0.5, upper=1.0,
                           strict_lower=True, strict_upper=True)
    if not assumptions:
        raise PowerDeclarationError("derivation requires explicit assumptions")
    z_alpha = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    z_power = NormalDist().inv_cdf(power)
    required = max(2, ceil(((z_alpha + z_power) * scale / mde) ** 2))
    return PowerDeclaration(
        protocol_hash=protocol_hash,
        status=PowerStatus.DERIVED_FROM_DECLARED_ASSUMPTIONS,
        minimum_detectable_effect=mde,
        baseline_scale=scale,
        significance_level=alpha,
        desired_power=power,
        required_observations=required,
        method="TWO_SIDED_NORMAL_APPROXIMATION_DECLARED_ASSUMPTIONS_ONLY",
        assumptions=assumptions,
    )


def power_from_mapping(protocol_hash: str, payload: Mapping[str, Any] | None) -> PowerDeclaration:
    if payload is None:
        return unknown_power(protocol_hash)
    if not isinstance(payload, Mapping):
        raise PowerDeclarationError("power declaration must be a mapping")
    allowed = {
        "status", "minimum_detectable_effect", "baseline_scale", "significance_level",
        "desired_power", "required_observations", "method", "assumptions",
    }
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise PowerDeclarationError("unexpected power fields: " + ",".join(unknown))
    return PowerDeclaration(
        protocol_hash=protocol_hash,
        status=PowerStatus(payload.get("status", "UNKNOWN")),
        minimum_detectable_effect=payload.get("minimum_detectable_effect"),
        baseline_scale=payload.get("baseline_scale"),
        significance_level=payload.get("significance_level"),
        desired_power=payload.get("desired_power"),
        required_observations=payload.get("required_observations"),
        method=payload.get("method"),
        assumptions=tuple(payload.get("assumptions") or ()),
    )
