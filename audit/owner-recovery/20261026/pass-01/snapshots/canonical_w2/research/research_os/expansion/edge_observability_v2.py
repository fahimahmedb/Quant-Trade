from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Optional

from .evidence_acquisition_intents_v2 import build_evidence_acquisition_intents


SCHEMA_VERSION = "oracle-v2-edge-observability-v1"
CLOSED_AUTHORITY = {
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
}
_FORBIDDEN_OUTCOME_KEYS = {
    "return",
    "returns",
    "pnl",
    "profit",
    "loss",
    "outcome",
    "outcomes",
    "evaluation_result",
    "portfolio_contribution",
}


class EdgeObservabilityError(ValueError):
    """Raised when a projection input violates the pre-outcome truth boundary."""


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(payload).hexdigest()


def _assert_pre_outcome(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        authority = value.get("authority")
        if isinstance(authority, Mapping):
            for key, expected in CLOSED_AUTHORITY.items():
                if authority.get(key, expected) is not False:
                    raise EdgeObservabilityError(f"AUTHORITY_OPEN_IN_PROJECTION:{path}.authority.{key}")
        if "outcome_accessed" in value and value.get("outcome_accessed") is not False:
            raise EdgeObservabilityError(f"OUTCOME_ACCESS_VISIBLE_TO_PROJECTION:{path}.outcome_accessed")
        if "economic_result" in value and value.get("economic_result") not in (None, "NOT_OBSERVED"):
            raise EdgeObservabilityError(f"ECONOMIC_RESULT_VISIBLE_TO_PROJECTION:{path}.economic_result")
        for key, child in value.items():
            if str(key).lower() in _FORBIDDEN_OUTCOME_KEYS:
                raise EdgeObservabilityError(f"OUTCOME_FIELD_VISIBLE_TO_PROJECTION:{path}.{key}")
            _assert_pre_outcome(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_pre_outcome(child, f"{path}[{index}]")


def _dossier_vector(research: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    raw = (((research or {}).get("dossier") or {}).get("dossier") or {})
    fields: Dict[str, Dict[str, Any]] = {}
    for name, detail in sorted(raw.items()):
        if not isinstance(detail, Mapping):
            continue
        status = str(detail.get("status", "UNKNOWN"))
        limitations = list(detail.get("limitations") or [])
        fields[name] = {
            "status": status,
            "limitations": limitations,
            "has_support": detail.get("support") is not None,
        }
    counts = {
        "SUPPORTED": sum(item["status"] == "SUPPORTED" for item in fields.values()),
        "PARTIAL": sum(item["status"] == "PARTIAL" for item in fields.values()),
        "UNKNOWN": sum(item["status"] == "UNKNOWN" for item in fields.values()),
        "OTHER": sum(item["status"] not in {"SUPPORTED", "PARTIAL", "UNKNOWN"} for item in fields.values()),
    }
    missing = [
        {"field": name, "status": detail["status"], "limitations": detail["limitations"]}
        for name, detail in fields.items()
        if detail["status"] != "SUPPORTED"
    ]
    return {
        "fields": fields,
        "counts": counts,
        "missing_evidence": missing,
        "fully_supported": bool(fields) and not missing,
    }


def _collect_blockers(
    research: Optional[Mapping[str, Any]],
    readiness: Optional[Mapping[str, Any]],
    negative_memory: Optional[Mapping[str, Any]],
) -> list[str]:
    blockers: list[str] = []
    if research:
        if research.get("blocker"):
            blockers.append(str(research["blocker"]))
        dossier = research.get("dossier") or {}
        blockers.extend(str(item) for item in (dossier.get("blockers") or []))
        screen = research.get("screen") or {}
        blockers.extend(str(item) for item in (screen.get("block_reasons") or []))
    if readiness:
        blockers.extend(str(item) for item in (readiness.get("blockers") or readiness.get("block_reasons") or []))
    if negative_memory and negative_memory.get("failure_reason"):
        blockers.append("NEGATIVE_MEMORY:" + str(negative_memory["failure_reason"]))
    return sorted(set(blockers))


def _maturity(
    *,
    research: Optional[Mapping[str, Any]],
    disconfirmation: Optional[Mapping[str, Any]],
    frozen_candidate: Optional[Mapping[str, Any]],
    validator: Optional[Mapping[str, Any]],
    readiness: Optional[Mapping[str, Any]],
    export_intent: Optional[Mapping[str, Any]],
) -> tuple[str, str]:
    experiment_readiness = "READY" if (
        (readiness or {}).get("status") == "READY" or export_intent is not None
    ) else "INCOMPLETE"
    validator_pass = (
        (validator or {}).get("scientific_decision") == "PASS"
        or (validator or {}).get("decision") == "PASS"
    )
    if export_intent is not None or experiment_readiness == "READY" or validator_pass:
        return "VALIDATED", experiment_readiness
    if frozen_candidate is not None:
        return "FROZEN", experiment_readiness
    if (disconfirmation or {}).get("attempted") is True:
        return "DISCONFIRMATION_ATTEMPTED", experiment_readiness
    if research and (research.get("candidate") or research.get("engine_output") or research.get("dossier")):
        return "EVIDENCE_BOUND", experiment_readiness
    return "IDEA", experiment_readiness


def build_edge_observability_projection(
    *,
    task: Mapping[str, Any],
    research: Optional[Mapping[str, Any]] = None,
    disconfirmation: Optional[Mapping[str, Any]] = None,
    frozen_candidate: Optional[Mapping[str, Any]] = None,
    validator: Optional[Mapping[str, Any]] = None,
    readiness: Optional[Mapping[str, Any]] = None,
    negative_memory: Optional[Mapping[str, Any]] = None,
    export_intent: Optional[Mapping[str, Any]] = None,
    producer_readiness: Optional[Dict[str, Any]] = None,
    declared_routes: Optional[list[Dict[str, Any]]] = None,
    validated_adapters: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Project V2 research truth without becoming a new source of truth.

    All inputs are caller-supplied durable artifacts. This function performs no
    fetch, write, observation, evaluation, or trading action. It deliberately
    reports scientific/process maturity rather than economic success.

    Optional producer readiness is distinct from V2 validation ``readiness``.
    Its explicit catalogs are passed to the existing CP008 bridge. Missing
    catalogs mean no declared route/adapter, never implicit source discovery.
    Acquisition planning does not advance scientific or experiment maturity.
    """
    inputs = {
        "task": task,
        "research": research,
        "disconfirmation": disconfirmation,
        "frozen_candidate": frozen_candidate,
        "validator": validator,
        "readiness": readiness,
        "negative_memory": negative_memory,
        "export_intent": export_intent,
        "producer_readiness": producer_readiness,
        "declared_routes": declared_routes,
        "validated_adapters": validated_adapters,
    }
    _assert_pre_outcome(inputs)

    task_id = str(task.get("task_id") or "")
    task_type = str(task.get("task_type") or "UNKNOWN")
    if not task_id:
        raise EdgeObservabilityError("TASK_ID_REQUIRED")
    if producer_readiness is None and (declared_routes is not None or validated_adapters is not None):
        raise EdgeObservabilityError("PRODUCER_READINESS_REQUIRED_FOR_ACQUISITION")

    acquisition = None
    if producer_readiness is not None:
        hypothesis_id = producer_readiness.get("hypothesis_id")
        # Do not silently join an intent for one hypothesis to another's edge.
        for record in (task, research or {}, (research or {}).get("candidate") or {}, frozen_candidate or {}):
            if record.get("hypothesis_id") and record["hypothesis_id"] != hypothesis_id:
                raise EdgeObservabilityError("ACQUISITION_HYPOTHESIS_BINDING_MISMATCH")
        intents = build_evidence_acquisition_intents(
            producer_readiness,
            declared_routes=declared_routes if declared_routes is not None else [],
            validated_adapters=validated_adapters if validated_adapters is not None else {},
        )
        rows = []
        for intent in intents["intents"]:
            plan = intent["acquisition_plan"] or {}
            rows.append({
                "requirement": intent["requirement"],
                "status": intent["status"],
                "blockers": deepcopy(intent["blockers"]),
                "adapter_id": intent.get("adapter_id"),
                "adapter_hash": intent.get("adapter_hash"),
                "declared_route_hash": intent.get("declared_route_hash"),
                "request_id": (intent["request"] or {}).get("request_id"),
                "firewall_status": plan.get("status", "NOT_PLANNED"),
                "firewall_blockers": deepcopy(plan.get("blockers", [])),
                "plan_hash": plan.get("plan_hash"),
                "execution_mode": (plan.get("plan") or {}).get("execution_mode"),
            })
        acquisition = {
            "hypothesis_id": intents["hypothesis_id"],
            "readiness_hash": intents["readiness_hash"],
            "intent_projection_hash": intents["projection_hash"],
            "status": intents["status"],
            "requirements": deepcopy(intents["requirements"]),
            "summary": deepcopy(intents["summary"]),
            "intents": rows,
            "interpretation": "PLAN_READINESS_IS_NOT_EVIDENCE_ACQUIRED",
            "network_execution_authorized": intents["network_execution_authorized"],
            "network_call_performed": intents["network_call_performed"],
            "network_connectivity": "NOT_INSPECTED",
        }

    blockers = _collect_blockers(research, readiness, negative_memory)
    scientific_maturity, experiment_readiness = _maturity(
        research=research,
        disconfirmation=disconfirmation,
        frozen_candidate=frozen_candidate,
        validator=validator,
        readiness=readiness,
        export_intent=export_intent,
    )
    evidence = _dossier_vector(research)

    if blockers:
        operational_state = "BLOCKED"
        interpretation = "BLOCKED_NOT_FAILED"
    elif export_intent is not None or experiment_readiness == "READY":
        operational_state = "READY_PACKAGE"
        interpretation = "READY_IS_NOT_PROFITABLE"
    elif scientific_maturity != "IDEA":
        operational_state = "ADVANCING"
        interpretation = "PRE_OUTCOME_RESEARCH_ONLY"
    else:
        operational_state = "NOT_STARTED"
        interpretation = "UNEXECUTED_NOT_NEGATIVE"

    research_dossier = (research or {}).get("dossier") or {}
    claim_ceiling = (
        (readiness or {}).get("claim_ceiling")
        or ("READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY" if export_intent is not None else None)
        or research_dossier.get("claim_ceiling")
        or "DESIGN_ONLY"
    )

    stages = {
        "research_attempted": research is not None,
        "disconfirmation_attempted": (disconfirmation or {}).get("attempted") is True,
        "frozen": frozen_candidate is not None,
        "validator_present": validator is not None,
        "readiness_present": readiness is not None,
        "export_intent_present": export_intent is not None,
        "negative_memory_present": negative_memory is not None,
    }

    projection = {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "task_type": task_type,
        "family": task_type,
        "scientific_maturity": scientific_maturity,
        "experiment_readiness": experiment_readiness,
        "operational_state": operational_state,
        "interpretation": interpretation,
        "claim_ceiling": claim_ceiling,
        "evidence_maturity": evidence,
        "blockers": blockers,
        "stages": stages,
        "economic_result": "NOT_OBSERVED",
        "empirical_correlation": "UNKNOWN",
        "marginal_portfolio_contribution": "NOT_ESTIMATED",
        "authority": deepcopy(CLOSED_AUTHORITY),
        "outcome_accessed": False,
        "projection_only": True,
        "source_of_truth": "CALLER_SUPPLIED_DURABLE_ARTIFACTS",
    }
    if acquisition is not None:
        projection["evidence_acquisition"] = acquisition
    projection["projection_hash"] = _canonical_hash(projection)
    return projection
