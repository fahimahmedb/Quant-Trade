from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable


REQUIRED_CANDIDATE_FIELDS = {
    "hypothesis_id",
    "generation_id",
    "mechanism",
    "claim",
    "falsification_scope",
    "decision_map",
    "economic_tags",
}


@dataclass(frozen=True)
class EngineContext:
    run_id: str
    synthetic_only: bool = True


class EngineContractError(ValueError):
    pass


def build_candidate(*, engine_id: str, engine_family: str, hypothesis_id: str,
                    mechanism: str, claim: str, falsification_scope: str,
                    decision_map: Dict[str, str], economic_tags: Iterable[str],
                    source_refs: Iterable[str], horizon: str,
                    context: EngineContext, documentary_evidence: Dict[str, Any] = None) -> Dict[str, Any]:
    if not context.synthetic_only and documentary_evidence is None:
        raise EngineContractError("documentary mode requires qualified captured evidence")
    candidate = {
        "hypothesis_id": hypothesis_id,
        "generation_id": "G1",
        "mechanism": mechanism,
        "claim": claim,
        "falsification_scope": falsification_scope,
        "decision_map": dict(decision_map),
        "economic_tags": sorted(set(economic_tags)),
        "horizon": horizon,
        "research_decision": "EXPLORE",
        "evidence_timing": "UNDETERMINED",
        "observation_authorization": "NOT_AUTHORIZED",
    }
    if documentary_evidence is not None:
        candidate['documentary_evidence'] = documentary_evidence
    output = {
        "engine_id": engine_id,
        "engine_family": engine_family,
        "synthetic_only": context.synthetic_only,
        "source_refs": list(source_refs),
        "candidate": candidate,
    }
    validate_engine_output(output)
    return output


def validate_engine_output(output: Dict[str, Any]) -> None:
    if type(output.get('synthetic_only')) is not bool:
        raise EngineContractError('engine evidence mode must be explicit')
    if output.get('synthetic_only') is False:
        from research.research_os.expansion.engine_dossiers_v1 import qualify_document_packet
        evidence = output.get('candidate', {}).get('documentary_evidence') or {}
        packet = evidence.get('packet') or {}
        if packet.get('evidence_class') != 'DOCUMENTARY':
            raise EngineContractError('documentary evidence cannot be inferred from synthetic input')
        qualification = qualify_document_packet(packet, output.get('engine_family'), evidence.get('freeze_time'))
        if qualification['status'] != 'PASS':
            raise EngineContractError(','.join(qualification['blockers']))
        if output.get('source_refs') != [packet.get('source_ref')]:
            raise EngineContractError('documentary source references must match the capture')
    if not output.get("engine_id") or not output.get("engine_family"):
        raise EngineContractError("missing engine identity")
    refs = output.get("source_refs") or []
    if not refs:
        raise EngineContractError("source_refs cannot be empty")
    candidate = output.get("candidate") or {}
    missing = REQUIRED_CANDIDATE_FIELDS - candidate.keys()
    if missing:
        raise EngineContractError(f"candidate missing fields: {sorted(missing)}")
    if len(candidate["decision_map"]) < 2:
        raise EngineContractError("decision_map must distinguish at least two outcomes")
    if not candidate["economic_tags"]:
        raise EngineContractError("economic_tags cannot be empty")
