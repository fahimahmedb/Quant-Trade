"""F-sourced pure identity primitives for verified continuity.

This is deliberately not the GIGA-F feeder, registry, scheduler, proposal writer,
or an activation surface.  It only preserves the missing root/variant/exposure
identity laws needed to prevent cohort relabeling from resetting scientific
history.  Persistence remains owned by the existing Research OS ledgers.
"""
from __future__ import annotations

from typing import Any, Mapping

from ..expansion.v2_core import canonical_hash

UNKNOWN = "UNKNOWN"
_ROOT_FIELDS = (
    "mechanism", "actor", "universe", "clock", "horizon",
    "payer", "economic_exposure", "instrument",
)


def _norm(value: Any) -> Any:
    if value is None:
        return UNKNOWN
    if isinstance(value, str):
        text = " ".join(value.strip().lower().split())
        return text if text and text.upper() != UNKNOWN else UNKNOWN
    if isinstance(value, Mapping):
        return {str(k): _norm(value[k]) for k in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_norm(item) for item in value]
    if isinstance(value, (bool, int, float)):
        return value
    return str(value)


def root_identity(semantic_identity: Mapping[str, Any]) -> dict[str, Any]:
    """Return cohort/label/source-version independent scientific root identity."""
    if not isinstance(semantic_identity, Mapping):
        raise ValueError("ROOT_IDENTITY_MAPPING_REQUIRED")
    identity = {field: _norm(semantic_identity.get(field)) for field in _ROOT_FIELDS}
    if any(identity[field] == UNKNOWN for field in ("mechanism", "actor", "universe", "clock", "horizon")):
        raise ValueError("ROOT_IDENTITY_CRITICAL_FIELD_UNKNOWN")
    return identity


def root_hypothesis_id(semantic_identity: Mapping[str, Any]) -> str:
    """Stable across cohorts, branch labels and source-version churn."""
    return "root:" + canonical_hash(root_identity(semantic_identity))


def variant_id(root_id: str, parameters: Any) -> str:
    if not isinstance(root_id, str) or not root_id.startswith("root:"):
        raise ValueError("ROOT_ID_REQUIRED")
    return "variant:" + canonical_hash({"root_hypothesis_id": root_id, "parameters": _norm(parameters or {})})


def exposure_id(root_id: str, *, kind: str, reference: str) -> str:
    if not isinstance(root_id, str) or not root_id.startswith("root:"):
        raise ValueError("ROOT_ID_REQUIRED")
    if not isinstance(kind, str) or not kind.strip() or not isinstance(reference, str) or not reference.strip():
        raise ValueError("EXPOSURE_IDENTITY_REQUIRED")
    return "exposure:" + canonical_hash({
        "root_hypothesis_id": root_id,
        "kind": kind.strip().upper(),
        "reference": reference.strip(),
    })


def bind_identity(semantic_identity: Mapping[str, Any], *, parameters: Any = None) -> dict[str, Any]:
    root = root_hypothesis_id(semantic_identity)
    return {
        "root_hypothesis_id": root,
        "variant_id": variant_id(root, parameters or {}),
        "root_identity": root_identity(semantic_identity),
    }
