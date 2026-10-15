from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List
from datetime import datetime
from decimal import Decimal, InvalidOperation

from research.research_os.scientific_store import sha256_json
from research.research_os.engines.protocol import EngineContractError, build_candidate


DOCUMENT_FACTS = {
    "FUNDAMENTAL": {"revenue", "operating_income", "operating_cash_flow", "capital_expenditure"},
    "EVENT_DOCUMENT": {"previous_low", "previous_high", "current_low", "current_high"},
    "QUANT_MECHANISM": {"constrained_quantity", "eligible_quantity"},
    "INSTITUTIONAL_FLOW": {"constrained_quantity", "eligible_quantity"},
    "EDGE_ARCHAEOLOGY": {"constrained_quantity", "eligible_quantity"},
}


def _clock(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("document clocks must include a timezone")
    return parsed


def qualify_document_packet(packet: Dict[str, Any], family: str, freeze_time: str) -> Dict[str, Any]:
    """Qualify an outcome-free structured input, not a live source connector.

    The stable engine contract still requires synthetic_only=True. Real captured
    documents need a separately reviewed adapter-contract migration, not relabeling.
    """
    required = {"evidence_class", "source_ref", "issuer_id", "published_at", "available_at",
                "revision_status", "period", "unit", "facts", "content_hash"}
    optional = {"actor", "constraint", "instrument", "horizon"}
    blockers = []
    if required - packet.keys() or packet.keys() - required - optional:
        blockers.append("DOCUMENT_FIELDS_INVALID")
    if packet.get("evidence_class") != "SYNTHETIC" or not str(packet.get("source_ref", "")).startswith("synthetic://"):
        blockers.append("DOCUMENT_CLASS_OUTSIDE_STABLE_ENGINE_CONTRACT")
    if packet.get("revision_status") != "ORIGINAL_AS_PUBLISHED":
        blockers.append("DOCUMENT_REVISION_NOT_QUALIFIED")
    for field in ("issuer_id", "period", "unit"):
        if not isinstance(packet.get(field), str) or not packet[field].strip() or packet[field] == "UNKNOWN":
            blockers.append(f"DOCUMENT_{field.upper()}_MISSING")
    payload = {k: v for k, v in packet.items() if k != "content_hash"}
    if packet.get("content_hash") != sha256_json(payload):
        blockers.append("DOCUMENT_HASH_MISMATCH")
    try:
        published, available, freeze = (_clock(v) for v in (packet["published_at"], packet["available_at"], freeze_time))
        if not published <= available <= freeze:
            blockers.append("DOCUMENT_CLOCK_NOT_PIT")
    except (KeyError, TypeError, ValueError, AttributeError):
        blockers.append("DOCUMENT_CLOCK_INVALID")
    facts = packet.get("facts", {})
    required_facts = DOCUMENT_FACTS.get(family)
    if required_facts is None or not isinstance(facts, dict) or set(facts) != required_facts:
        blockers.append("DOCUMENT_FACTS_INVALID")
    else:
        try:
            values = {k: Decimal(str(v)) for k, v in facts.items()}
            if not all(v.is_finite() for v in values.values()):
                raise ValueError("nonfinite fact")
            if family == "FUNDAMENTAL":
                if values["revenue"] <= 0 or values["capital_expenditure"] < 0:
                    raise ValueError("invalid statement magnitude")
            elif family == "EVENT_DOCUMENT":
                if any(values[f"{p}_low"] > values[f"{p}_high"] for p in ("previous", "current")):
                    raise ValueError("inverted guidance interval")
            else:
                if not 0 <= values["constrained_quantity"] <= values["eligible_quantity"] or values["eligible_quantity"] <= 0:
                    raise ValueError("invalid eligible population")
                if packet.get("unit") != "units":
                    raise ValueError("population units must be units")
                if any(not isinstance(packet.get(k), str) or not packet[k].strip() for k in optional):
                    raise ValueError("missing constraint identity")
        except (InvalidOperation, ValueError):
            blockers.append("DOCUMENT_FACT_VALUES_INVALID")
    return {"status": "BLOCK" if blockers else "PASS", "blockers": sorted(set(blockers)),
            "source_hash": packet.get("content_hash"), "evidence_class": "SYNTHETIC",
            "outcome_accessed": False}


def documentary_candidate(engine: Any, source: Dict[str, Any], context: Any, hypothesis_id: str) -> Dict[str, Any]:
    packet = source["documentary_packet"]
    freeze = source["freeze_time"]
    qualification = qualify_document_packet(packet, engine.family, freeze)
    if qualification["status"] != "PASS":
        raise EngineContractError(",".join(qualification["blockers"]))
    facts = {k: Decimal(str(v)) for k, v in packet["facts"].items()}
    issuer, period, unit = (packet[k] for k in ("issuer_id", "period", "unit"))
    if engine.family == "FUNDAMENTAL":
        margin = facts["operating_income"] / facts["revenue"]
        fcf = facts["operating_cash_flow"] - facts["capital_expenditure"]
        measurements = {"operating_margin": str(margin), "free_cash_flow": str(fcf)}
        mechanism = "Cash generation and operating profitability may support a valuation thesis; market pricing remains untested."
        claim = f"{issuer} {period}: operating margin={margin}; free cash flow={fcf} {unit}."
        disconfirm = "Withdraw the profitability premise if an admissible same-basis statement shows nonpositive margin or free cash flow."
        tags, horizon = ["quality", "cash_flow", "equity_beta"], "2q"
    elif engine.family == "EVENT_DOCUMENT":
        before = (facts["previous_low"] + facts["previous_high"]) / 2
        after = (facts["current_low"] + facts["current_high"]) / 2
        delta = after - before
        measurements = {"previous_midpoint": str(before), "current_midpoint": str(after), "guidance_change": str(delta)}
        mechanism = "A same-period guidance change may alter expectations; consensus surprise and price response remain untested."
        claim = f"{issuer} {period}: guidance midpoint changed by {delta} {unit}, from {before} to {after}."
        disconfirm = "Withdraw the revision premise if the document is corrected, superseded, or the periods/units differ."
        tags, horizon = ["guidance_revision", "information_processing", "equity_beta"], "1-20d"
    else:
        share = facts["constrained_quantity"] / facts["eligible_quantity"]
        measurements = {"constrained_share": str(share)}
        mechanism = f"{packet['actor']} faces {packet['constraint']} in {packet['instrument']}; pressure/reversal remains untested."
        claim = f"{issuer} {period}: declared constrained share={share} of {facts['eligible_quantity']} units."
        disconfirm = "Reject if the actor is not constrained, the universe is ineligible, or the legacy family has already spent this scope."
        tags, horizon = ["forced_flow", "liquidity", "constraint"], packet["horizon"]
    output = build_candidate(
        engine_id=engine.engine_id, engine_family=engine.family, hypothesis_id=hypothesis_id,
        mechanism=mechanism, claim=claim, falsification_scope=disconfirm,
        decision_map={"premise_survives": "EXPLORE", "premise_fails": "KILL_GENERATION"},
        economic_tags=tags, source_refs=[packet["source_ref"]], horizon=horizon, context=context,
    )
    output["candidate"]["documentary_evidence"] = {
        "packet": deepcopy(packet), "freeze_time": freeze, "measurements": measurements,
        "claim_source_hash": packet["content_hash"], "economic_result": "NOT_OBSERVED",
    }
    return output


REQUIRED_BY_FAMILY = {
    "QUANT_MECHANISM": {
        "trigger",
        "payer_or_forced_actor",
        "structural_reason",
        "expression",
        "universe_definition",
        "confounders",
        "disconfirmation_checks",
    },
    "FUNDAMENTAL": {
        "issuer_identity",
        "financial_statements",
        "earnings_and_guidance",
        "estimate_revisions",
        "valuation_frame",
        "balance_sheet_quality",
        "cash_flow_quality",
        "competitive_position",
        "catalysts",
        "disconfirmation_checks",
    },
    "EVENT_DOCUMENT": {
        "event_identity",
        "document_clock",
        "eligibility_rule",
        "novel_information",
        "diffusion_hypothesis",
        "confounders",
        "disconfirmation_checks",
    },
    "INSTITUTIONAL_FLOW": {
        "forced_actor",
        "constraint_rule",
        "implementation_clock",
        "affected_universe",
        "expected_footprint",
        "capacity_constraints",
        "confounders",
        "disconfirmation_checks",
    },
}


def build_engine_dossier(output: Dict[str, Any], detail_input: Dict[str, Any]) -> Dict[str, Any]:
    family = output["engine_family"]
    if family not in REQUIRED_BY_FAMILY:
        raise ValueError(f"unsupported deep-dossier family: {family}")
    candidate = output["candidate"]
    required = REQUIRED_BY_FAMILY[family]
    missing = sorted(field for field in required if detail_input.get(field) in (None, "", [], {}))
    blockers: List[str] = [f"MISSING_{field.upper()}" for field in missing]
    if detail_input.get("outcome_accessed") is not False:
        blockers.append("OUTCOME_ACCESS_NOT_ALLOWED")
    if detail_input.get("source_clock_frozen") is not True:
        blockers.append("SOURCE_CLOCK_NOT_FROZEN")
    if detail_input.get("active_disconfirmation") is not True:
        blockers.append("ACTIVE_DISCONFIRMATION_MISSING")

    dossier = {
        "hypothesis_id": candidate["hypothesis_id"],
        "generation_id": candidate["generation_id"],
        "engine_id": output["engine_id"],
        "engine_family": family,
        "mechanism": candidate["mechanism"],
        "claim": candidate["claim"],
        "falsification_scope": candidate["falsification_scope"],
        "horizon": candidate.get("horizon"),
        "source_refs": list(output.get("source_refs") or []),
        "dossier": deepcopy(detail_input),
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": blockers,
        "candidate_mutated": False,
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
    }
    return dossier


def build_engine_dossiers(
    outputs: Iterable[Dict[str, Any]],
    detail_by_hypothesis: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []
    for output in outputs:
        family = output["engine_family"]
        if family not in REQUIRED_BY_FAMILY:
            continue
        hid = output["candidate"]["hypothesis_id"]
        records.append(build_engine_dossier(output, detail_by_hypothesis[hid]))
    return {
        "engine_depth_version": "engine-dossiers.v1",
        "record_count": len(records),
        "records": records,
        "pass_count": sum(item["status"] == "PASS" for item in records),
        "block_count": sum(item["status"] != "PASS" for item in records),
        "economic_results_observed": 0,
        "candidate_mutations": 0,
    }
