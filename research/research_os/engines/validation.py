from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, Iterable, List


REQUIRED_CANDIDATE_FIELDS = (
    "hypothesis_id",
    "generation_id",
    "mechanism",
    "claim",
    "falsification_scope",
    "decision_map",
    "economic_tags",
    "observation_authorization",
)


def independent_validate(engine_output: Dict[str, Any]) -> Dict[str, Any]:
    candidate = engine_output["candidate"]
    failures = []
    for field in REQUIRED_CANDIDATE_FIELDS:
        if field not in candidate or candidate[field] in (None, "", [], {}):
            failures.append(f"missing:{field}")
    if engine_output.get("synthetic_only") is not True:
        failures.append("non_synthetic_input")
    if candidate.get("observation_authorization") != "NOT_AUTHORIZED":
        failures.append("unauthorized_observation_state")
    if len(engine_output.get("source_refs") or []) < 1:
        failures.append("missing_provenance")
    return {
        "hypothesis_id": candidate.get("hypothesis_id"),
        "validator": "independent-validator.v0",
        "status": "PASS" if not failures else "BLOCK",
        "failures": failures,
        "evidence": {
            "mechanism": "PRESENT" if candidate.get("mechanism") else "MISSING",
            "data_integrity": "SYNTHETIC_FIXTURE",
            "statistical": "NOT_ASSESSED",
            "economic": "NOT_ASSESSED",
            "prospective": "NOT_ASSESSED",
        },
    }


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def red_team(outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
    pairwise = []
    blocked = []
    for left, right in combinations(outputs, 2):
        lc, rc = left["candidate"], right["candidate"]
        overlap = round(_jaccard(lc["economic_tags"], rc["economic_tags"]), 4)
        relation = "INDEPENDENT"
        if lc["mechanism"] == rc["mechanism"]:
            relation = "SAME_MECHANISM"
        elif overlap >= 0.5:
            relation = "RELATED_MECHANISM"
        elif overlap >= 0.25:
            relation = "POSSIBLE_EXPOSURE_OVERLAP"
        pairwise.append({
            "left": lc["hypothesis_id"],
            "right": rc["hypothesis_id"],
            "economic_tag_overlap": overlap,
            "relation": relation,
        })
        if relation == "SAME_MECHANISM":
            blocked.append(f"duplicate_mechanism:{lc['hypothesis_id']}:{rc['hypothesis_id']}")

    return {
        "red_team": "red-team.v0",
        "status": "BLOCK" if blocked else "PASS",
        "negative_rights": [
            "BLOCK_DATA",
            "BLOCK_LEAKAGE",
            "BLOCK_MULTIPLICITY",
            "BLOCK_COST_MODEL",
            "BLOCK_CAPACITY",
            "BLOCK_CLAIM_LEVEL",
        ],
        "blocks": blocked,
        "pairwise": pairwise,
    }
