"""Adversarial net-economic-value gate for paper/shadow decisions.

This module deliberately does not choose scientific protocol parameters.  It
consumes a versioned effect estimate and predeclared economic inputs, keeps
every friction inside the decision function, and fails closed when executable
capacity or parameter provenance is not established.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math


class Decision(str, Enum):
    CONTINUE = "CONTINUE"
    NO_TRADE = "NO_TRADE"
    KILL = "KILL"


@dataclass(frozen=True)
class ModelParameter:
    """One immutable model input and the evidence that fixes its value."""

    name: str
    value: float
    unit: str
    source: str
    as_of: str
    version: str

    def validate(self) -> None:
        if not self.name or not self.unit or not self.source or not self.as_of or not self.version:
            raise ValueError(f"incomplete provenance for parameter {self.name!r}")
        if not math.isfinite(self.value):
            raise ValueError(f"non-finite parameter {self.name!r}")


@dataclass(frozen=True)
class CostInput:
    """Expected forward market/deployment cost (never a sunk program cost)."""

    parameter: ModelParameter
    amount: float
    applies: bool = True

    def validate(self) -> None:
        self.parameter.validate()
        if self.amount < 0 or not math.isfinite(self.amount):
            raise ValueError(f"invalid cost amount for {self.parameter.name!r}")
        if self.parameter.unit != "currency":
            raise ValueError(f"cost {self.parameter.name!r} must use currency units")


@dataclass(frozen=True)
class EconomicInputs:
    """Frozen inputs for one prospective paper/shadow economic assessment."""

    assessment_id: str
    effect_id: str
    effect_version: str
    expected_gross_effect: float
    effect_uncertainty: float
    requested_exposure: float
    executable_capacity: float
    capacity_source: ModelParameter
    costs: tuple[CostInput, ...]
    economic_margin_rate: ModelParameter
    min_net_value: ModelParameter
    mode: str = "SHADOW"


@dataclass(frozen=True)
class EconomicAssessment:
    assessment_id: str
    decision: Decision
    reason_codes: tuple[str, ...]
    executable_exposure: float
    conservative_effect: float
    gross_value: float
    forward_cost: float
    uncertainty_charge: float
    economic_margin: float
    expected_net_value: float
    input_fingerprint: str


class EconomicEngine:
    """Map effect -> executable exposure -> conservative net value -> action."""

    REQUIRED_COSTS = frozenset(
        {"commission", "spread", "slippage", "impact", "latency", "financing", "borrow", "turnover"}
    )

    def assess(self, inputs: EconomicInputs) -> EconomicAssessment:
        self._validate(inputs)
        capacity = min(inputs.requested_exposure, inputs.executable_capacity)
        costs = {c.parameter.name: c.amount if c.applies else 0.0 for c in inputs.costs}
        forward_cost = sum(costs.values())
        uncertainty_charge = capacity * inputs.effect_uncertainty
        conservative_effect = inputs.expected_gross_effect - inputs.effect_uncertainty
        gross_value = capacity * inputs.expected_gross_effect
        margin = capacity * inputs.economic_margin_rate.value
        net = gross_value - forward_cost - uncertainty_charge - margin

        reasons: list[str] = []
        if capacity <= 0:
            decision = Decision.NO_TRADE
            reasons.append("NO_EXECUTABLE_CAPACITY")
        elif conservative_effect <= 0:
            decision = Decision.KILL
            reasons.append("EFFECT_DOES_NOT_SURVIVE_UNCERTAINTY")
        elif net < 0:
            decision = Decision.KILL
            reasons.append("ECONOMICALLY_DOMINATED_AFTER_FRICTIONS")
        elif net < inputs.min_net_value.value:
            decision = Decision.NO_TRADE
            reasons.append("INSUFFICIENT_NET_ECONOMIC_VALUE")
        else:
            decision = Decision.CONTINUE
            reasons.append("POSITIVE_CONSERVATIVE_NET_VALUE")
        if capacity < inputs.requested_exposure:
            reasons.append("CAPACITY_CLIPPED")

        return EconomicAssessment(
            assessment_id=inputs.assessment_id,
            decision=decision,
            reason_codes=tuple(reasons),
            executable_exposure=capacity,
            conservative_effect=conservative_effect,
            gross_value=gross_value,
            forward_cost=forward_cost,
            uncertainty_charge=uncertainty_charge,
            economic_margin=margin,
            expected_net_value=net,
            input_fingerprint=self._fingerprint(inputs),
        )

    def _validate(self, inputs: EconomicInputs) -> None:
        if inputs.mode not in {"PAPER", "SHADOW"}:
            raise ValueError("economic engine has no real-capital authority")
        if not inputs.assessment_id or not inputs.effect_id or not inputs.effect_version:
            raise ValueError("assessment and versioned effect identity are required")
        for name, value in (
            ("expected_gross_effect", inputs.expected_gross_effect),
            ("effect_uncertainty", inputs.effect_uncertainty),
            ("requested_exposure", inputs.requested_exposure),
            ("executable_capacity", inputs.executable_capacity),
        ):
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        inputs.capacity_source.validate()
        inputs.economic_margin_rate.validate()
        inputs.min_net_value.validate()
        if inputs.capacity_source.unit != "currency" or inputs.economic_margin_rate.unit != "return":
            raise ValueError("capacity must be currency and economic margin must be return")
        if inputs.min_net_value.unit != "currency" or inputs.min_net_value.value < 0:
            raise ValueError("minimum net value must be non-negative currency")
        if inputs.economic_margin_rate.value < 0:
            raise ValueError("economic margin cannot be negative")
        names = [cost.parameter.name for cost in inputs.costs]
        if len(names) != len(set(names)):
            raise ValueError("duplicate friction component")
        missing = self.REQUIRED_COSTS.difference(names)
        extra = set(names).difference(self.REQUIRED_COSTS)
        if missing or extra:
            raise ValueError(f"friction schema mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
        for cost in inputs.costs:
            cost.validate()

    @staticmethod
    def _fingerprint(inputs: EconomicInputs) -> str:
        def parameter(p: ModelParameter) -> dict[str, object]:
            return {"name": p.name, "value": p.value, "unit": p.unit, "source": p.source,
                    "as_of": p.as_of, "version": p.version}

        payload = {
            "assessment_id": inputs.assessment_id,
            "effect_id": inputs.effect_id,
            "effect_version": inputs.effect_version,
            "expected_gross_effect": inputs.expected_gross_effect,
            "effect_uncertainty": inputs.effect_uncertainty,
            "requested_exposure": inputs.requested_exposure,
            "executable_capacity": inputs.executable_capacity,
            "capacity_source": parameter(inputs.capacity_source),
            "costs": [{"parameter": parameter(c.parameter), "amount": c.amount, "applies": c.applies}
                      for c in sorted(inputs.costs, key=lambda item: item.parameter.name)],
            "economic_margin_rate": parameter(inputs.economic_margin_rate),
            "min_net_value": parameter(inputs.min_net_value),
            "mode": inputs.mode,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        return hashlib.sha256(encoded).hexdigest()
