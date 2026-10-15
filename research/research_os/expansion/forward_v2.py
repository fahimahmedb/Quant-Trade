from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict

from research.research_os.scientific_store import sha256_json


ALLOWED_STATES = {
    "DRAFT",
    "READY_AWAITING_OWNER_AUTHORITY",
    "AUTHORIZED_FOR_EXACT_SCOPE",
    "CLOSED",
}


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_forward_contract_v2(
    registration: Dict[str, Any],
    *,
    t0: str,
    observation_scope: Dict[str, Any],
) -> Dict[str, Any]:
    readiness = registration.get("readiness")
    state = "READY_AWAITING_OWNER_AUTHORITY" if readiness == "READY_AWAITING_OWNER_AUTHORITY" else "DRAFT"
    payload = {
        "contract_id": registration["prospective_contract_id"],
        "hypothesis_id": registration["hypothesis_id"],
        "generation_id": registration["generation_id"],
        "protocol_hash": registration.get("protocol_hash"),
        "t0": t0,
        "observation_scope": deepcopy(observation_scope),
        "material_change_requires_new_generation": True,
    }
    return {
        **payload,
        "state": state,
        "contract_hash": sha256_json(payload),
        "owner_authorization": "NOT_AUTHORIZED",
        "authorization_scope_hash": None,
        "observation_count": 0,
        "future_outcomes_consumed": 0,
        "economic_result": "NOT_OBSERVED",
    }


class ForwardRegistryV2:
    def __init__(self) -> None:
        self._contracts: Dict[str, Dict[str, Any]] = {}

    def register(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        contract_id = contract["contract_id"]
        current = self._contracts.get(contract_id)
        if current is not None:
            if current["contract_hash"] != contract["contract_hash"]:
                raise ValueError(f"forward contract mutation rejected: {contract_id}")
            return deepcopy(current)
        if contract["state"] not in ALLOWED_STATES:
            raise ValueError("invalid forward state")
        if contract["material_change_requires_new_generation"] is not True:
            raise ValueError("material changes must create a new generation")
        self._contracts[contract_id] = deepcopy(contract)
        return deepcopy(contract)

    def validate_observation_candidate(self, contract_id: str, observation_meta: Dict[str, Any]) -> Dict[str, Any]:
        contract = self._contracts[contract_id]
        if contract["state"] != "AUTHORIZED_FOR_EXACT_SCOPE":
            raise PermissionError("forward observation requires exact Owner authorization")
        observed_at = _parse_utc(observation_meta["observed_at"])
        if observed_at <= _parse_utc(contract["t0"]):
            raise ValueError("prospective observation must occur strictly after t0")
        supplied_scope_hash = sha256_json(observation_meta["scope"])
        if supplied_scope_hash != contract["authorization_scope_hash"]:
            raise PermissionError("observation scope does not match Owner-authorized scope")
        return {
            "contract_id": contract_id,
            "status": "ADMISSIBLE_CHRONOLOGICALLY",
            "observed_at": observation_meta["observed_at"],
            "outcome_consumed": False,
        }

    def snapshot(self) -> Dict[str, Any]:
        entries = [deepcopy(self._contracts[key]) for key in sorted(self._contracts)]
        return {
            "registry_id": "forward-registry.v2",
            "entry_count": len(entries),
            "entries": entries,
            "authorized_count": sum(item["state"] == "AUTHORIZED_FOR_EXACT_SCOPE" for item in entries),
            "observation_count": sum(item["observation_count"] for item in entries),
            "future_outcomes_consumed": sum(item["future_outcomes_consumed"] for item in entries),
            "immutable_generations": True,
        }
