from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


class AppendOnlyHashLedger:
    def __init__(self) -> None:
        self.entries: List[Dict[str, Any]] = []

    def append(self, kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        previous_hash = self.entries[-1]["entry_hash"] if self.entries else None
        envelope = {
            "seq": len(self.entries) + 1,
            "kind": kind,
            "previous_hash": previous_hash,
            "payload_hash": sha256_json(payload),
            "payload": payload,
        }
        envelope["entry_hash"] = sha256_json({
            "seq": envelope["seq"],
            "kind": kind,
            "previous_hash": previous_hash,
            "payload_hash": envelope["payload_hash"],
        })
        self.entries.append(envelope)
        return envelope

    def verify(self) -> bool:
        previous_hash = None
        for index, entry in enumerate(self.entries, 1):
            if entry.get("seq") != index:
                return False
            if entry.get("previous_hash") != previous_hash:
                return False
            if entry.get("payload_hash") != sha256_json(entry.get("payload")):
                return False
            expected = sha256_json({
                "seq": index,
                "kind": entry.get("kind"),
                "previous_hash": previous_hash,
                "payload_hash": entry.get("payload_hash"),
            })
            if entry.get("entry_hash") != expected:
                return False
            previous_hash = entry["entry_hash"]
        return True

    def write_jsonl(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(canonical_json(entry) + "\n" for entry in self.entries))


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
