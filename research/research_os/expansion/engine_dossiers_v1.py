from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List


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
