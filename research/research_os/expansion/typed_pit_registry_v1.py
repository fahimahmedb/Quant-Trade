from __future__ import annotations

from copy import deepcopy
from threading import RLock
import json
import re

from research.research_os.scientific_store import sha256_json
from .acquisition_firewall_v1 import FORBIDDEN_CONTENT_CLASSES
from typing import Any, Dict, Iterable, List


def _contains_outcome(value: Any) -> bool:
    if isinstance(value, dict):
        return any((isinstance(key, str) and key.strip().lower() in FORBIDDEN_CONTENT_CLASSES)
                   or _contains_outcome(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(_contains_outcome(item) for item in value)
    return False


class TypedPITRegistry:
    def __init__(self) -> None:
        self._entries: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()

    def register(
        self,
        typed_record: Dict[str, Any],
        provenance_manifest: Dict[str, Any],
    ) -> Dict[str, Any]:
        with self._lock:
            if typed_record.get("status") != "PASS":
                raise ValueError("typed PIT record must PASS before registration")
            if provenance_manifest.get("status") != "PASS":
                raise ValueError("provenance manifest must PASS before registration")
            if typed_record.get("outcome_accessed") is not False:
                raise ValueError("outcome-bearing PIT record forbidden")
            if typed_record.get("network_origin") is not False:
                raise ValueError("network-origin record forbidden in Wave 4")
            typed_fields = ("record_id", "source_version_id", "effective_at", "published_at",
                            "captured_at", "content_classes", "payload", "adapter_id", "plan_hash",
                            "record_origin", "raw_record_hash")
            try:
                body = {key: typed_record[key] for key in typed_fields}
                json.dumps(body, allow_nan=False)
                if (not isinstance(body["payload"], dict) or _contains_outcome(body["payload"])
                        or not isinstance(body["content_classes"], list)
                        or not body["content_classes"]
                        or any(not isinstance(v, str) or v in FORBIDDEN_CONTENT_CLASSES
                               for v in body["content_classes"])):
                    raise ValueError("outcome-bearing or malformed typed PIT content")
                manifest = provenance_manifest["manifest"]
                if (typed_record["typed_record_hash"] != sha256_json(body)
                        or provenance_manifest["manifest_hash"] != sha256_json(manifest)):
                    raise ValueError("typed PIT proof hash mismatch")
                for manifest_key, typed_key in (
                    ("record_id", "record_id"), ("source_version_id", "source_version_id"),
                    ("published_at", "published_at"), ("captured_at", "captured_at"),
                    ("adapter_id", "adapter_id"), ("adapter_plan_hash", "plan_hash"),
                    ("typed_record_hash", "typed_record_hash"), ("raw_record_hash", "raw_record_hash"),
                ):
                    if manifest.get(manifest_key) != typed_record[typed_key]:
                        raise ValueError("typed PIT manifest binding mismatch")
                if (typed_record.get("point_in_time_record") is not True
                        or typed_record.get("record_origin") != "SYNTHETIC_FIXTURE_ONLY"
                        or manifest.get("origin") != "SYNTHETIC_FIXTURE_ONLY"
                        or provenance_manifest.get("network_accessed") is not False
                        or provenance_manifest.get("outcome_accessed") is not False):
                    raise ValueError("typed PIT provenance is not fixture-only")
                for key in ("raw_record_hash", "plan_hash"):
                    if not isinstance(body[key], str) or not re.fullmatch(r"[0-9a-f]{64}", body[key]):
                        raise ValueError("typed PIT reference hash invalid")
            except (KeyError, TypeError, AttributeError) as exc:
                raise ValueError("typed PIT proof malformed") from exc
            record_id = typed_record.get("record_id")
            if not isinstance(record_id, str) or not record_id:
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
        with self._lock:
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
