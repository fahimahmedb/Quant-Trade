from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List

from research.research_os.scientific_store import sha256_json


ALLOWED_DATA_CLASSES = {
    "REGULATORY_FILINGS",
    "CORPORATE_IR",
    "OFFICIAL_MACRO",
    "EXCHANGE_REFERENCE",
    "PUBLIC_INDEX_RULES",
    "OFFICIAL_CORPORATE_ACTIONS",
}
ALLOWED_ACTIVATION_STATES = {"DESIGN_ONLY_NOT_CONNECTED", "FIXTURE_ONLY"}


def validate_adapter_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    required = {
        "adapter_id",
        "provider_family",
        "data_class",
        "permission_model",
        "clock_semantics",
        "revision_policy",
        "survivorship_policy",
        "locator_template",
        "activation_state",
        "network_access",
        "contains_market_outcome",
    }
    for field in sorted(required - spec.keys()):
        blockers.append(f"MISSING_{field.upper()}")
    if spec.get("data_class") not in ALLOWED_DATA_CLASSES:
        blockers.append("DATA_CLASS_NOT_ALLOWED")
    if spec.get("activation_state") not in ALLOWED_ACTIVATION_STATES:
        blockers.append("ACTIVATION_STATE_NOT_ALLOWED")
    if spec.get("network_access") is not False:
        blockers.append("NETWORK_ACCESS_FORBIDDEN_IN_WAVE3")
    if spec.get("contains_market_outcome") is not False:
        blockers.append("OUTCOME_BEARING_ADAPTER_FORBIDDEN")
    for field in ("permission_model", "clock_semantics", "revision_policy", "survivorship_policy", "locator_template"):
        if spec.get(field) in (None, "", "UNKNOWN"):
            blockers.append(f"{field.upper()}_UNKNOWN")

    canonical = {
        "adapter_id": spec.get("adapter_id"),
        "provider_family": spec.get("provider_family"),
        "data_class": spec.get("data_class"),
        "permission_model": spec.get("permission_model"),
        "clock_semantics": spec.get("clock_semantics"),
        "revision_policy": spec.get("revision_policy"),
        "survivorship_policy": spec.get("survivorship_policy"),
        "locator_template": spec.get("locator_template"),
        "activation_state": spec.get("activation_state"),
        "network_access": spec.get("network_access"),
        "contains_market_outcome": spec.get("contains_market_outcome"),
        "allowed_content": sorted(spec.get("allowed_content") or []),
        "forbidden_content": sorted(spec.get("forbidden_content") or []),
    }
    return {
        "adapter_id": spec.get("adapter_id"),
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": sorted(set(blockers)),
        "adapter_hash": sha256_json(canonical),
        "canonical_spec": canonical,
        "network_access": False,
        "outcome_access_authorized": False,
        "activated": False,
    }


class DesignOnlyAdapterRegistry:
    def __init__(self) -> None:
        self._entries: Dict[str, Dict[str, Any]] = {}

    def register(self, validated: Dict[str, Any]) -> Dict[str, Any]:
        adapter_id = validated.get("adapter_id")
        if not adapter_id:
            raise ValueError("adapter_id required")
        current = self._entries.get(adapter_id)
        if current is not None:
            if current["adapter_hash"] != validated["adapter_hash"]:
                raise ValueError(f"adapter mutation rejected: {adapter_id}")
            return deepcopy(current)
        self._entries[adapter_id] = deepcopy(validated)
        return deepcopy(validated)

    def register_many(self, records: Iterable[Dict[str, Any]]) -> None:
        for record in records:
            self.register(record)

    def snapshot(self) -> Dict[str, Any]:
        entries = [deepcopy(self._entries[key]) for key in sorted(self._entries)]
        return {
            "registry_id": "design-only-source-adapters.v1",
            "entry_count": len(entries),
            "entries": entries,
            "activated_count": sum(bool(item["activated"]) for item in entries),
            "network_enabled_count": sum(bool(item["network_access"]) for item in entries),
            "outcome_authorized_count": sum(bool(item["outcome_access_authorized"]) for item in entries),
            "immutable": True,
        }
