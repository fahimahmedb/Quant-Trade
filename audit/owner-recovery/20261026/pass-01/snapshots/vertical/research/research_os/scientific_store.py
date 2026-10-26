from __future__ import annotations

import hashlib
import json
import os
import tempfile
from copy import deepcopy
from threading import RLock
from pathlib import Path
from typing import Any, Dict, Iterable, List


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _ledger_payload(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("ledger payload must be an object")

    def check_keys(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ValueError("ledger object keys must be strings")
                check_keys(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                check_keys(item)

    check_keys(payload)
    # Freeze the JSON representation used by both hashing and persistence.
    return json.loads(json.dumps(payload, allow_nan=False, ensure_ascii=False))


class AppendOnlyHashLedger:
    def __init__(self) -> None:
        self.entries: List[Dict[str, Any]] = []
        self._lock = RLock()

    def append(self, kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            if not isinstance(kind, str) or not kind:
                raise ValueError("ledger kind must be a nonempty string")
            frozen = _ledger_payload(payload)
            if not self.verify():
                raise ValueError("cannot extend an invalid ledger")
            previous_hash = self.entries[-1]["entry_hash"] if self.entries else None
            envelope = {
                "seq": len(self.entries) + 1,
                "kind": kind,
                "previous_hash": previous_hash,
                "payload_hash": sha256_json(frozen),
                "payload": frozen,
            }
            envelope["entry_hash"] = sha256_json({
                "seq": envelope["seq"],
                "kind": kind,
                "previous_hash": previous_hash,
                "payload_hash": envelope["payload_hash"],
            })
            self.entries.append(envelope)
            return deepcopy(envelope)

    def verify(self) -> bool:
        with self._lock:
            if not isinstance(self.entries, list):
                return False
            previous_hash = None
            try:
                for index, entry in enumerate(self.entries, 1):
                    if not isinstance(entry, dict) or set(entry) != {
                        "seq", "kind", "previous_hash", "payload_hash", "payload", "entry_hash"
                    }:
                        return False
                    if type(entry["seq"]) is not int or entry["seq"] != index:
                        return False
                    if not isinstance(entry["kind"], str) or not entry["kind"]:
                        return False
                    if entry["previous_hash"] != previous_hash:
                        return False
                    payload = _ledger_payload(entry["payload"])
                    if entry["payload_hash"] != sha256_json(payload):
                        return False
                    expected = sha256_json({
                        "seq": index,
                        "kind": entry["kind"],
                        "previous_hash": previous_hash,
                        "payload_hash": entry["payload_hash"],
                    })
                    if entry["entry_hash"] != expected:
                        return False
                    previous_hash = entry["entry_hash"]
            except (TypeError, ValueError, OverflowError, RecursionError):
                return False
            return True

    def write_jsonl(self, path: Path) -> None:
        with self._lock:
            if not self.verify():
                raise ValueError("cannot publish an invalid ledger")
            content = "".join(canonical_json(entry) + "\n" for entry in self.entries)
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, staging = tempfile.mkstemp(prefix=".scientific-ledger-", dir=path.parent)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(staging, path)
                directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
            finally:
                if os.path.exists(staging):
                    os.unlink(staging)


def scientific_snapshot(*, run_id: str, candidate: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    hid = candidate["hypothesis_id"]
    gid = candidate["generation_id"]
    return {
        "ledger_entry_id": f"{run_id}:{hid}:{gid}",
        "hypothesis_generation_id": f"{hid}-{gid}",
        "lifecycle": "PREREGISTERED",
        "research_decision": candidate.get("research_decision", "EXPLORE"),
        "refs": {
            "hypothesis": f"memory://{hid}/{gid}",
            "trial_ledger": f"memory://trial/{hid}/{gid}",
            "experiment_results": [],
            "evidence_assessments": [],
            "decision_records": [],
            "prospective_contracts": [],
            "economic_identity": None,
            "portfolio_map_entry": None,
            "negative_knowledge": [],
        },
        "open_blockers": ["ECONOMIC_EXPERIMENT_NOT_AUTHORIZED"],
        "updated_at": timestamp,
    }


def trial_record(*, run_id: str, candidate: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    hid = candidate["hypothesis_id"]
    gid = candidate["generation_id"]
    return {
        "trial_record_id": f"{run_id}:trial:{hid}:{gid}",
        "hypothesis_id": hid,
        "generation_id": gid,
        "observed_attempt_count": 1,
        "estimated_effective_trials": None,
        "effective_trials_status": "UNKNOWN",
        "method": None,
        "assumptions": [],
        "covered_scope": "synthetic engine generation only",
        "limitations": ["No economic outcome inspected", "Effective-trial denominator not inferred"],
        "attempt_refs": [f"synthetic://{run_id}/{hid}/{gid}/engine-output"],
        "failed_run_refs": [],
        "abandoned_attempt_refs": [],
        "manual_exploratory_refs": [],
        "updated_at": timestamp,
    }


def build_scientific_ledgers(*, run_id: str, outputs: Iterable[Dict[str, Any]], timestamp: str) -> Dict[str, Any]:
    ledger = AppendOnlyHashLedger()
    trial_records: List[Dict[str, Any]] = []
    for output in outputs:
        candidate = output["candidate"]
        snapshot = scientific_snapshot(run_id=run_id, candidate=candidate, timestamp=timestamp)
        trial = trial_record(run_id=run_id, candidate=candidate, timestamp=timestamp)
        ledger.append("SCIENTIFIC_SNAPSHOT", snapshot)
        ledger.append("TRIAL_RECORD", trial)
        trial_records.append(trial)
    return {
        "scientific_ledger": ledger,
        "trial_records": trial_records,
    }
