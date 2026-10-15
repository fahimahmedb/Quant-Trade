from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List


class TypedPITRegistry:
    def __init__(self) -> None:
        self._entries: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        typed_record: Dict[str, Any],
        provenance_manifest: Dict[str, Any],
    ) -> Dict[str, Any]:
        if typed_record.get("status") != "PASS":
            raise ValueError("typed PIT record must PASS before registration")
        if provenance_manifest.get("status") != "PASS":
            raise ValueError("provenance manifest must PASS before registration")
        if typed_record.get("outcome_accessed") is not False:
            raise ValueError("outcome-bearing PIT record forbidden")
        if typed_record.get("network_origin") is not False:
            raise ValueError("network-origin record forbidden in Wave 4")
        record_id = typed_record.get("record_id")
        if not record_id:
            raise ValueError("record_id required")
        envelope = {
            "record_id": record_id,
            "typed_record_hash": typed_record["typed_record_hash"],
            "manifest_hash": provenance_manifest["manifest_hash"],
            "source_version_id": typed_record["source_version_id"],
            "published_at": typed_record["published_at"],
            "captured_at": typed_record["captured_at"],
            "adapter_id": typed_record["adapter_id"],
            "point_in_time_record": True,
            "outcome_accessed": False,
            "network_origin": False,
        }
        current = self._entries.get(record_id)
        if current is not None:
            if (
                current["typed_record_hash"] != envelope["typed_record_hash"]
                or current["manifest_hash"] != envelope["manifest_hash"]
            ):
                raise ValueError(f"typed PIT record mutation rejected: {record_id}")
            return deepcopy(current)
        self._entries[record_id] = deepcopy(envelope)
        return deepcopy(envelope)

    def register_many(
        self,
        pairs: Iterable[tuple[Dict[str, Any], Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        return [self.register(record, manifest) for record, manifest in pairs]

    def snapshot(self) -> Dict[str, Any]:
        entries = [deepcopy(self._entries[key]) for key in sorted(self._entries)]
        return {
            "registry_id": "typed-pit-registry.v1",
            "entry_count": len(entries),
            "entries": entries,
            "point_in_time_count": sum(bool(item["point_in_time_record"]) for item in entries),
            "network_origin_count": sum(bool(item["network_origin"]) for item in entries),
            "outcome_accessed_count": sum(bool(item["outcome_accessed"]) for item in entries),
            "immutable": True,
        }
