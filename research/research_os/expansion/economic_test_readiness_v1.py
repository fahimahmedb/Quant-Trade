"""CP069-first convergence facade for W1 Factory economic readiness.

New compositions reuse the qualified W1 Factory registry/runner/firewall chain,
while the CP069 freeze contract remains authoritative for implementation binding
and synthetic-scope law. Historical frozen CP069 receipts keep their original
recheck path during the migration interval.
"""
from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Any, Mapping

from . import _economic_test_readiness_cp069 as _cp069
from . import _economic_test_readiness_factory as _factory
from .final_shape import freeze_experiment_envelope as _cp069_freeze_experiment_envelope


AUTHORITY = dict(_cp069.AUTHORITY)
READY = _cp069.READY
_FREEZE_ADAPTER_LOCK = RLock()


def _freeze_with_cp069(output, implementation, experiment_meta):
    meta = deepcopy(experiment_meta)
    # CP069 law: the implementation declaration is frozen into protocol identity.
    meta["implementability_declaration"] = deepcopy(implementation)
    return _cp069_freeze_experiment_envelope(output, implementation, meta)


def _synthetic_scope_blockers(package: Any) -> list[str]:
    if not isinstance(package, Mapping):
        return ["PRODUCER_SYNTHETIC_SCOPE_INVALID"]
    output = package.get("engine_output")
    output = output if isinstance(output, Mapping) else {}
    blockers: list[str] = []
    if type(output.get("synthetic_only")) is not bool:
        blockers.append("PRODUCER_SYNTHETIC_SCOPE_INVALID")

    sources = package.get("sources")
    if isinstance(sources, list):
        for source in sources:
            route = source.get("route") if isinstance(source, Mapping) else None
            if not isinstance(route, Mapping):
                continue
            fixture_only = (
                route.get("source_class") == "SYNTHETIC_FIXTURE"
                or route.get("permission_state") == "FIXTURE_ONLY"
            )
            if fixture_only and output.get("synthetic_only") is not True:
                blockers.append("FIXTURE_SOURCE_REQUIRES_SYNTHETIC_SCOPE")
                break
    return blockers


def _apply_cp069_postconditions(result: Any, package: Any, blockers: list[str]):
    if not isinstance(result, dict):
        return {
            "status": "BLOCK",
            "block_reasons": ["INVALID_FACTORY_READINESS_RESULT"],
            "authority": dict(AUTHORITY),
            "outcome_accessed": False,
            "economic_result": "NOT_OBSERVED",
            "architecture_stop_build": False,
        }

    merged = sorted(set(list(result.get("block_reasons") or []) + blockers))
    if merged:
        result["status"] = "BLOCK"
        result["block_reasons"] = merged
        result["remaining_execution_blockers"] = merged
        result["architecture_stop_build"] = False

    output = package.get("engine_output") if isinstance(package, Mapping) else None
    result["synthetic_only"] = (
        output.get("synthetic_only") if isinstance(output, Mapping) else None
    )
    # Convergence must never create authority.
    result["authority"] = dict(AUTHORITY)
    result["outcome_accessed"] = False
    result["economic_result"] = "NOT_OBSERVED"
    return result


def economic_test_readiness(
    package, *, legacy, frozen=None, peer_identities=(), red_team_context=None
):
    # Migration compatibility: a persisted CP069 receipt without Factory
    # infrastructure is rechecked by the exact CP069 implementation. The
    # canonical validator it calls is still the converged fail-closed facade.
    if isinstance(frozen, Mapping) and "experiment_infrastructure" not in frozen:
        return _cp069.economic_test_readiness(
            package,
            legacy=legacy,
            frozen=frozen,
            peer_identities=peer_identities,
            red_team_context=red_team_context,
        )

    blockers = _synthetic_scope_blockers(package)

    # The W1 Factory composer imported freeze_experiment_envelope by name.
    # Adapt that private binding narrowly and restore it even on failure.
    with _FREEZE_ADAPTER_LOCK:
        original = _factory.freeze_experiment_envelope
        _factory.freeze_experiment_envelope = _freeze_with_cp069
        try:
            result = _factory.economic_test_readiness(
                package,
                legacy=legacy,
                frozen=frozen,
                peer_identities=peer_identities,
                red_team_context=red_team_context,
            )
        finally:
            _factory.freeze_experiment_envelope = original

    return _apply_cp069_postconditions(result, package, blockers)
