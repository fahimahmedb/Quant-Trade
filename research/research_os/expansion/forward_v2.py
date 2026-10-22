from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict
from pathlib import Path
from threading import RLock

from research.research_os.scientific_store import sha256_json


ALLOWED_STATES = {
    "DRAFT",
    "READY_AWAITING_OWNER_AUTHORITY",
    "AUTHORIZED_FOR_EXACT_SCOPE",
    "CLOSED",
}


def _require_forward_identity(payload: Dict[str, Any]) -> None:
    for key in ("contract_id", "hypothesis_id", "generation_id"):
        value = payload.get(key)
        if (not isinstance(value, str) or not value.strip()
                or value.strip().upper() in {"UNKNOWN", "UNRESOLVED", "NOT_APPLICABLE", "NONE", "NULL"}):
            raise ValueError("forward identity invalid: " + key)


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("forward clocks must include a timezone")
    return parsed.astimezone(timezone.utc)


def build_forward_contract_v2(
    registration: Dict[str, Any],
    *,
    t0: str,
    observation_scope: Dict[str, Any],
) -> Dict[str, Any]:
    _parse_utc(t0)
    if not isinstance(observation_scope, dict) or not observation_scope:
        raise ValueError("forward scope cannot be empty")
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
    _require_forward_identity(payload)
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
        self._lock = RLock()

    def register(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            payload_fields = ("contract_id", "hypothesis_id", "generation_id", "protocol_hash", "t0",
                              "observation_scope", "material_change_requires_new_generation")
            expected_fields = set(payload_fields) | {'state', 'contract_hash', 'owner_authorization',
                'authorization_scope_hash', 'observation_count', 'future_outcomes_consumed', 'economic_result'}
            if set(contract) != expected_fields:
                raise ValueError('forward contract fields invalid')
            payload = {k: contract[k] for k in payload_fields}
            _require_forward_identity(payload)
            if contract.get("contract_hash") != sha256_json(payload):
                raise ValueError("forward contract hash mismatch")
            _parse_utc(contract['t0'])
            if not isinstance(contract['observation_scope'], dict) or not contract['observation_scope']:
                raise ValueError("forward scope cannot be empty")
            if (contract.get('state') not in {'DRAFT', 'READY_AWAITING_OWNER_AUTHORITY', 'CLOSED'}
                    or contract.get('owner_authorization') != 'NOT_AUTHORIZED'
                    or contract.get('authorization_scope_hash') is not None
                    or type(contract.get('observation_count')) is not int or contract['observation_count'] != 0
                    or type(contract.get('future_outcomes_consumed')) is not int or contract['future_outcomes_consumed'] != 0
                    or contract.get('economic_result') != 'NOT_OBSERVED'):
                raise PermissionError("build registry cannot import observation authority or outcomes")
            if contract['state'] == 'READY_AWAITING_OWNER_AUTHORITY' and not contract['protocol_hash']:
                raise ValueError("ready registration requires a frozen protocol")
            contract_id = contract["contract_id"]
            for other_id, other in self._contracts.items():
                if other_id != contract_id and (other['hypothesis_id'], other['generation_id']) == (contract['hypothesis_id'], contract['generation_id']):
                    raise ValueError("same generation cannot be registered under a second contract id")
            current = self._contracts.get(contract_id)
            if current is not None:
                if current != contract:
                    raise ValueError(f"forward contract mutation rejected: {contract_id}")
                return deepcopy(current)
            if contract["state"] not in ALLOWED_STATES:
                raise ValueError("invalid forward state")
            if contract["material_change_requires_new_generation"] is not True:
                raise ValueError("material changes must create a new generation")
            self._contracts[contract_id] = deepcopy(contract)
            return deepcopy(contract)

    def save(self, path: Path) -> None:
        from .persistent_state import write_immutable_json
        write_immutable_json(path, self.snapshot())

    @classmethod
    def load(cls, path: Path) -> 'ForwardRegistryV2':
        from .persistent_state import read_immutable_json
        snapshot = read_immutable_json(path)
        registry = cls()
        for entry in snapshot['entries']:
            registry.register(entry)
        if registry.snapshot() != snapshot:
            raise ValueError("forward snapshot summary mismatch")
        return registry

    def validate_observation_candidate(self, contract_id: str, observation_meta: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
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
        with self._lock:
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
