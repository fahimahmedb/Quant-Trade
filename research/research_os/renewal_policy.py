"""Fixed/preregistered bounded Research OS cohort-renewal contract.

This is a pure policy membrane owned by the existing Research OS/Control surface.
It does not create tasks, activate a feed, allocate a new budget, execute science,
or mutate the queue. Operational renewal remains disabled.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Mapping

from .expansion.v2_core import canonical_hash

RENEWAL_OPERATIONALLY_ENABLED = False
REQUIRED_FIELDS = (
    "PROGRAM_ID", "COHORT_ID", "PREDECESSOR_COHORT_ID", "PREDECESSOR_CLOSURE_RECEIPT",
    "CLOSURE_REASON", "SUCCESSOR_ELIGIBILITY_REASON", "INFORMATION_CUTOFF",
    "QUALIFIED_SOURCE_VERSIONS", "QUESTION_DISTRIBUTION", "SOURCE_FAMILY_DISTRIBUTION",
    "ROOT_BUDGET", "VARIANT_BUDGET", "CUMULATIVE_PROGRAM_BUDGET", "CUMULATIVE_EXPOSURE",
    "VALIDATION_CAPACITY", "STOP_RULES", "REOPEN_RULES", "PROTECTED_OUTCOME_BOUNDARY",
    "AUTHORITY_SCOPE", "EFFECTIVE_CLOCK", "SCIENTIFIC_EPOCH_ID", "IDEMPOTENCY_KEY",
)
_BUDGET_FIELDS = ("ROOT_BUDGET", "VARIANT_BUDGET", "CUMULATIVE_PROGRAM_BUDGET", "VALIDATION_CAPACITY")
_CLOSED_AUTHORITY = (
    "economic_experiment_authorized", "prospective_observation_authorized",
    "real_capital_authorized", "live_trading_authorized",
)


class RenewalContractError(ValueError):
    pass


def _known(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().upper() not in {"UNKNOWN", "UNRESOLVED", "NONE", "N/A"}
    return True


def _time(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise RenewalContractError("RENEWAL_CLOCK_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RenewalContractError("RENEWAL_CLOCK_INVALID") from exc
    if parsed.tzinfo is None:
        raise RenewalContractError("RENEWAL_CLOCK_TIMEZONE_REQUIRED")
    return parsed


def _policy_body(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: deepcopy(contract.get(key))
        for key in (
            "PROGRAM_ID", "QUESTION_DISTRIBUTION", "SOURCE_FAMILY_DISTRIBUTION",
            "ROOT_BUDGET", "VARIANT_BUDGET", "CUMULATIVE_PROGRAM_BUDGET",
            "VALIDATION_CAPACITY", "STOP_RULES", "REOPEN_RULES",
            "PROTECTED_OUTCOME_BOUNDARY", "AUTHORITY_SCOPE",
        )
    }


def _policy_hash(contract: Mapping[str, Any]) -> str:
    return canonical_hash(_policy_body(contract))


def validate_contract(contract: Mapping[str, Any], *, predecessor: Mapping[str, Any] | None = None,
                      expected_policy_hash: str | None = None) -> dict[str, Any]:
    if not isinstance(contract, Mapping):
        raise RenewalContractError("RENEWAL_CONTRACT_MAPPING_REQUIRED")
    row = deepcopy(dict(contract))
    missing = [field for field in REQUIRED_FIELDS if field not in row or row.get(field) is None]
    if missing:
        raise RenewalContractError("RENEWAL_FIELDS_MISSING:" + ",".join(missing))
    scalar_required = (
        "PROGRAM_ID", "COHORT_ID", "PREDECESSOR_COHORT_ID", "PREDECESSOR_CLOSURE_RECEIPT",
        "CLOSURE_REASON", "SUCCESSOR_ELIGIBILITY_REASON", "INFORMATION_CUTOFF",
        "PROTECTED_OUTCOME_BOUNDARY", "EFFECTIVE_CLOCK", "SCIENTIFIC_EPOCH_ID", "IDEMPOTENCY_KEY",
    )
    bad_scalar = [field for field in scalar_required if not _known(row.get(field))]
    if bad_scalar:
        raise RenewalContractError("RENEWAL_SCALAR_FIELD_UNKNOWN:" + ",".join(bad_scalar))
    if row.get("POLICY_MODE", "FIXED_PREREGISTERED") != "FIXED_PREREGISTERED":
        raise RenewalContractError("ADAPTIVE_RENEWAL_POLICY_FORBIDDEN")
    if row.get("OPERATIONALLY_ENABLED") not in (None, False):
        raise RenewalContractError("RENEWAL_OPERATIONAL_ACTIVATION_FORBIDDEN")
    authority = row.get("AUTHORITY_SCOPE")
    if not isinstance(authority, Mapping) or any(authority.get(key) is not False for key in _CLOSED_AUTHORITY):
        raise RenewalContractError("RENEWAL_AUTHORITY_MUST_REMAIN_CLOSED")
    if row.get("PROTECTED_OUTCOME_BOUNDARY") not in {"SEALED", "OUTCOME_BLIND", "PRE_OUTCOME_ONLY"}:
        raise RenewalContractError("PROTECTED_OUTCOME_BOUNDARY_INVALID")
    info_cutoff = _time(row["INFORMATION_CUTOFF"])
    effective = _time(row["EFFECTIVE_CLOCK"])
    if effective < info_cutoff:
        raise RenewalContractError("RENEWAL_EFFECTIVE_BEFORE_INFORMATION_CUTOFF")

    calculated = _policy_hash(row)
    supplied = row.get("POLICY_HASH")
    if supplied not in (None, calculated):
        raise RenewalContractError("RENEWAL_POLICY_HASH_MISMATCH")
    if expected_policy_hash is not None and calculated != expected_policy_hash:
        raise RenewalContractError("STALE_RENEWAL_POLICY_HASH")
    row["POLICY_HASH"] = calculated

    sources = row.get("QUALIFIED_SOURCE_VERSIONS")
    if not isinstance(sources, (list, tuple)):
        raise RenewalContractError("QUALIFIED_SOURCE_VERSIONS_SEQUENCE_REQUIRED")
    exposures = row.get("CUMULATIVE_EXPOSURE")
    if not isinstance(exposures, (list, tuple)) or len(set(map(str, exposures))) != len(exposures):
        raise RenewalContractError("CUMULATIVE_EXPOSURE_MUST_BE_UNIQUE_SEQUENCE")

    if predecessor is not None:
        prior = validate_contract(predecessor)
        if row["PROGRAM_ID"] != prior["PROGRAM_ID"]:
            raise RenewalContractError("RENEWAL_PROGRAM_ID_CHANGED")
        if row["PREDECESSOR_COHORT_ID"] != prior["COHORT_ID"]:
            raise RenewalContractError("RENEWAL_PREDECESSOR_COHORT_MISMATCH")
        if row["COHORT_ID"] == prior["COHORT_ID"]:
            raise RenewalContractError("RENEWAL_SUCCESSOR_COHORT_MUST_DIFFER")
        for field in _BUDGET_FIELDS:
            if row[field] != prior[field]:
                raise RenewalContractError("OWNER_POLICY_DECISION_REQUIRED:" + field)
        prior_exposure = set(map(str, prior["CUMULATIVE_EXPOSURE"]))
        current_exposure = set(map(str, row["CUMULATIVE_EXPOSURE"]))
        if not prior_exposure.issubset(current_exposure):
            raise RenewalContractError("RENEWAL_EXPOSURE_RESET_FORBIDDEN")

        policy_changed = calculated != prior["POLICY_HASH"]
        prior_outcome_exposed = prior.get("OUTCOME_EXPOSURE_CHARGED") is True
        if prior_outcome_exposed and policy_changed and row["SCIENTIFIC_EPOCH_ID"] == prior["SCIENTIFIC_EPOCH_ID"]:
            raise RenewalContractError("POST_OUTCOME_POLICY_CHANGE_REQUIRES_NEW_SCIENTIFIC_EPOCH")
        if row["SCIENTIFIC_EPOCH_ID"] != prior["SCIENTIFIC_EPOCH_ID"]:
            if not _known(row.get("EPOCH_TRIGGERING_INFORMATION_SET")):
                raise RenewalContractError("NEW_SCIENTIFIC_EPOCH_TRIGGER_REQUIRED")
            if not prior_exposure.issubset(current_exposure):
                raise RenewalContractError("NEW_EPOCH_MUST_RETAIN_PRIOR_EXPOSURE")
        if row.get("COUNTS_AS_INDEPENDENT_CONFIRMATION") is True:
            raise RenewalContractError("COHORT_OR_EPOCH_RENAME_NOT_INDEPENDENT_CONFIRMATION")

    return row


def evaluate_successor(contract: Mapping[str, Any], *, predecessor: Mapping[str, Any] | None = None,
                       expected_policy_hash: str | None = None) -> dict[str, Any]:
    row = validate_contract(contract, predecessor=predecessor, expected_policy_hash=expected_policy_hash)
    sources = row["QUALIFIED_SOURCE_VERSIONS"]
    if not sources:
        return {
            "status": "PARK",
            "reason": "NO_ADMISSIBLE_QUALIFIED_SOURCE_VERSION",
            "program_id": row["PROGRAM_ID"],
            "cohort_id": row["COHORT_ID"],
            "idempotency_key": row["IDEMPOTENCY_KEY"],
            "policy_hash": row["POLICY_HASH"],
            "operationally_enabled": False,
            "scheduler_mutation": False,
            "authority_expanded": False,
        }
    return {
        "status": "BOUNDED_SUCCESSOR_ELIGIBLE_NOT_ACTIVATED",
        "program_id": row["PROGRAM_ID"],
        "cohort_id": row["COHORT_ID"],
        "predecessor_cohort_id": row["PREDECESSOR_COHORT_ID"],
        "scientific_epoch_id": row["SCIENTIFIC_EPOCH_ID"],
        "idempotency_key": row["IDEMPOTENCY_KEY"],
        "policy_hash": row["POLICY_HASH"],
        "cumulative_exposure": deepcopy(row["CUMULATIVE_EXPOSURE"]),
        "operationally_enabled": False,
        "scheduler_mutation": False,
        "authority_expanded": False,
    }
