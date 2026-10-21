"""Connect current frozen experiments to the canonical Factory integrity laws.

This module is deliberately pure. It does not persist a registry or own lifecycle
truth. It binds the current Canonical Research Core envelope/frozen protocol,
existing DryRunExperimentRunner plan/receipt/replay, and current trial accounting
into one immutable pre-outcome attestation.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .experiment_registry import (
    ExperimentLifecycle,
    ExperimentRegistryError,
    bind_execution_plan,
    bind_receipt,
    bind_replay,
    canonical_hash,
    create_registry_entry,
)
from .experiment_geometry import GeometryStatus, geometry_from_mapping
from .experiment_outcome_firewall import OutcomeFirewallError, assert_pre_outcome_payload
from .experiment_power import PowerStatus, power_from_mapping


class ExperimentInfrastructureError(ValueError):
    pass


def bind_pre_outcome_infrastructure(
    *,
    envelope: Mapping[str, Any],
    plan: Mapping[str, Any],
    replay: Mapping[str, Any] | None,
    trial_accounting: Mapping[str, Any],
    geometry_declaration: Mapping[str, Any] | None = None,
    power_declaration: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Bind exact current artifacts without creating a second truth store."""
    try:
        assert_pre_outcome_payload(envelope)
        assert_pre_outcome_payload(plan)
        assert_pre_outcome_payload(trial_accounting)
        if replay is not None:
            assert_pre_outcome_payload(replay)

        frozen_protocol = plan.get("frozen_protocol")
        binding_hashes = plan.get("binding_hashes")
        receipt = plan.get("pre_outcome_receipt")
        if not isinstance(frozen_protocol, Mapping):
            raise ExperimentInfrastructureError("FROZEN_PROTOCOL_REQUIRED")
        if not isinstance(binding_hashes, Mapping):
            raise ExperimentInfrastructureError("CANONICAL_BINDING_HASHES_REQUIRED")
        if not isinstance(receipt, Mapping):
            raise ExperimentInfrastructureError("PRE_OUTCOME_RECEIPT_REQUIRED")
        if plan.get("status") != "READY_FOR_REPRODUCIBLE_DRY_RUN":
            raise ExperimentInfrastructureError("EXECUTION_PLAN_NOT_READY")

        protocol_hash = envelope.get("protocol_hash")
        geometry = geometry_from_mapping(protocol_hash, geometry_declaration)
        power = power_from_mapping(protocol_hash, power_declaration)
        frozen_entry = create_registry_entry(
            envelope=envelope,
            frozen_protocol=frozen_protocol,
            binding_hashes=binding_hashes,
            trial_accounting=trial_accounting,
            geometry=geometry,
            power=power,
        )
        prepared = bind_execution_plan(frozen_entry, plan)
        receipt_bound = bind_receipt(prepared, receipt)
        final_entry = receipt_bound
        if replay is not None:
            final_entry = bind_replay(receipt_bound, replay)

        blockers: list[str] = []
        declaration_gaps: list[str] = []
        if geometry.status is GeometryStatus.UNKNOWN:
            declaration_gaps.append("GEOMETRY_DECLARATION_UNKNOWN")
        if power.status is PowerStatus.UNKNOWN:
            declaration_gaps.append("POWER_DECLARATION_UNKNOWN")
        if replay is None:
            blockers.append("EXPERIMENT_REPLAY_NOT_VERIFIED")

        qualified = not blockers and final_entry.lifecycle is ExperimentLifecycle.REPLAY_VERIFIED
        geometry_payload = {**geometry.to_dict(), "declaration_hash": geometry.declaration_hash}
        power_payload = {**power.to_dict(), "declaration_hash": power.declaration_hash}
        payload = {
            "status": "PASS" if qualified else "BLOCK",
            "qualification": "QUALIFIED_CURRENT" if qualified else "PARTIAL_WITH_EXPLICIT_BLOCKER",
            "scientific_declaration_state": "DECLARED_OR_EXPLICIT_UNKNOWN" if declaration_gaps else "DECLARED",
            "blockers": blockers,
            "declaration_gaps": declaration_gaps,
            "registry": final_entry.to_dict(),
            "frozen_registry": frozen_entry.to_dict(),
            "frozen_protocol": deepcopy(dict(frozen_protocol)),
            "execution_plan": deepcopy(dict(plan)),
            "replay": deepcopy(dict(replay)) if isinstance(replay, Mapping) else None,
            "geometry": geometry_payload,
            "power": power_payload,
            "outcome_accessed": False,
            "economic_result": "NOT_OBSERVED",
            "economic_experiment_authorized": False,
            "prospective_observation_authorized": False,
            "real_capital_authorized": False,
            "live_trading_authorized": False,
        }
        payload["infrastructure_hash"] = canonical_hash(payload)
        return payload
    except (ExperimentRegistryError, OutcomeFirewallError, ValueError, TypeError) as exc:
        if isinstance(exc, ExperimentInfrastructureError):
            raise
        raise ExperimentInfrastructureError(str(exc)) from exc


def assert_same_infrastructure(current: Mapping[str, Any], frozen: Mapping[str, Any]) -> None:
    """Fail closed when a previous readiness receipt is rebound to different infra."""
    for side, value in (("current", current), ("frozen", frozen)):
        if not isinstance(value, Mapping):
            raise ExperimentInfrastructureError(f"{side.upper()}_INFRASTRUCTURE_MISSING")
        assert_pre_outcome_payload(value)
    if current.get("infrastructure_hash") != frozen.get("infrastructure_hash"):
        raise ExperimentInfrastructureError("EXPERIMENT_INFRASTRUCTURE_BINDING_MISMATCH")
